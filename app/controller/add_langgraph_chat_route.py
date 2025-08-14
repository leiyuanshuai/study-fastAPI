from datetime import datetime
import json
from typing import Union, Annotated

from fastapi import FastAPI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.types import interrupt, Command
from pydantic import BaseModel, Field

from app.utils.llm_utils import create_llm
from app.utils.postgres_checkpointer import PostgresCheckpointerManager


@tool(name_or_callable="tool_get_datetime", description="一个用于获取当前时间的工具，没有参数")
def tool_get_datetime():
  return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool(name_or_callable="tool_book_hotel", description="一个用于预定酒店的工具")
def tool_book_hotel(
  hotel_name: Annotated[str, '酒店名称'],
  room_type: Annotated[str, '房间类型'],
  check_in_date: Annotated[str, '入住时间'],
) -> str:
  resume_data = interrupt({
    "title": "请确认酒店预定信息",
    "form": [
      {
        "field": "hotel_name",
        "type": "input",
        "label": "酒店名称",
        "required": True,
      },
      {
        "field": "room_type",
        "type": "select",
        "label": "客房类型",
        "options": [
          {"label": "标间", "value": "标间"},
          {"label": "单间", "value": "单间"},
          {"label": "双人间", "value": "双人间"},
        ],
        "required": True,
      },
      {
        "field": "check_in_date",
        "type": "date",
        "label": "入住时间",
      }
    ],
    "formData": {
      "hotel_name": hotel_name,
      "room_type": room_type,
      "check_in_date": check_in_date,
    }
  })
  if resume_data == "N":
    return f"用户选择取消预定酒店"

  old_book_data = {
    "hotel_name": hotel_name,
    "room_type": room_type,
    "check_in_date": check_in_date,
  }
  new_book_data: dict = resume_data

  change_field_list = [(k, v) for k, v in old_book_data.items() if old_book_data.get(k) != new_book_data.get(k)]

  return (f"用户已经更改参数，最新的为{json.dumps(new_book_data, ensure_ascii=False)}" if change_field_list else "") + "，结果为预定成功"


class ChatMessage(BaseModel):
  id: str = Field(..., description="消息id")
  type: str = Field(..., description="消息类型")
  content: str = Field(..., description="消息内容")


# 对话接口参数类型
class ChatParam(BaseModel):
  thread_id: str = Field(..., description="线程id")
  human_message: ChatMessage = Field(..., description="用户消息")


class ChatAgent:
  agent: Union[CompiledStateGraph, None] = None

  @staticmethod
  async def get_agent() -> CompiledStateGraph:
    if not ChatAgent.agent:
      ChatAgent.agent = create_react_agent(
        model=create_llm(),
        tools=[tool_book_hotel, tool_get_datetime],
        checkpointer=await PostgresCheckpointerManager.get_instance(),
        prompt="""
        你是一名擅长使用工具的智能助手，你需要根据用户问题来进行回答，请使用中文进行回答。
        当用户问题需要调用工具时再调用工具，否则按照你的知识来回答问题。
        某些工具会触发中断让用户来编辑工具执行参数，这些工具会将新的执行参数作为信息返回，你需要回复用户最新的信息
        """
      )
    return ChatAgent.agent

  @staticmethod
  async def chat(human_message: ChatMessage, thread_id: str):
    graph = await ChatAgent.get_agent()
    chat_state = await ChatAgent.get_chat_state(thread_id)
    chat_history_list = chat_state.get('messages')
    graph_state = await graph.ainvoke(
      {"messages": [HumanMessage(content=human_message.content, id=human_message.id)]},
      config={"configurable": {"thread_id": thread_id}}
    )
    return {
      **graph_state,
      # 这里之所以要+1，是因为我们认为这次的HumanMessage已经在chat_history_list中了，但是实际上并没有，所以这里要+1
      "messages": graph_state.get('messages')[len(chat_history_list) + 1:],
    }

  @staticmethod
  async def get_chat_state(thread_id: str):
    graph = await ChatAgent.get_agent() # graph是CompiledStateGraph类型
    # aget_state相当于graph.ainvoke() StateSnapshot类型对象
    graph_state = await graph.aget_state(config={"configurable": {"thread_id": thread_id}})
    print("graph_state22", graph_state)
    if graph_state.values.get('messages', None) is None:
      graph_state.values['messages'] = []

    """
    {
      "messages": []
      "__interrupt__": []
    }
    """
    return {
      **graph_state.values,
      "__interrupt__": graph_state.interrupts,
    }


def add_langgraph_chat_route(app: FastAPI):
  # 聊天接口
  @app.post("/langgraph/chat", tags=["/lg_chat"])
  async def langgraph_chat(chat_param: ChatParam):
    return await ChatAgent.chat(chat_param.human_message, chat_param.thread_id)

  @app.post("/langgraph/chat_resume/{thread_id}", tags=["/lg_chat"])
  async def langgraph_chat(body: dict, thread_id: str):
    graph = await ChatAgent.get_agent()
    chat_state = await ChatAgent.get_chat_state(thread_id)
    chat_history_list = chat_state.get('messages')
    graph_state = await graph.ainvoke(
      Command(resume=body.get('resume_data')),
      config={"configurable": {"thread_id": thread_id}}
    )
    return {
      **graph_state,
      # 这里不需要加1，因为我们并没有往messages中增加消息
      "messages": graph_state.get('messages')[len(chat_history_list):],
    }

  # 查询聊天记录
  @app.get("/langgraph/chat_state/{thread_id}", tags=["/lg_chat"])
  async def langgraph_chat(thread_id: str):
    return await ChatAgent.get_chat_state(thread_id)
