from sqlmodel import Field
from app.model.BasicModel import BasicModel
from app.utils.create_module_service import create_model_service

class LgChat(BasicModel, table=True):
  __tablename__ = "lg_chat"
  title: str = Field(default=None, max_length=255, description="聊天窗口标题")

LgChatService = create_model_service(LgChat)


