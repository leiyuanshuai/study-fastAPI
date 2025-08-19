import json

import requests
from langchain_core.embeddings import Embeddings


class CustomEmbeddings(Embeddings):
  """
  自定义文本嵌入类，用于将文本转换为向量表示
  继承自LangChain的Embeddings基类
  """

  def __init__(self, base_url, api_key, model):
    """
    初始化自定义嵌入类

    参数:
    base_url: API的基础URL
    api_key: 访问API所需的密钥
    model: 要使用的嵌入模型名称
    """
    self.base_url = base_url  # API基础URL
    self.api_key = api_key  # API访问密钥
    self.model = model  # 嵌入模型名称

  def embed_documents(self, texts):
    """
    将多个文档转换为嵌入向量

    参数:
    texts: 包含多个文本的列表

    返回:
    包含每个文本对应嵌入向量的列表
    """
    # 设置请求头，包括内容类型和认证信息
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {self.api_key}"
    }

    # 构建请求负载
    payload = {"input": texts, "model": self.model, "encoding_format": "float"}

    # 发送POST请求到嵌入API
    response = requests.post(
      f"{self.base_url}/embeddings",
      headers=headers,
      data=json.dumps(payload)
    )

    # 检查请求是否成功，如果失败则抛出异常
    response.raise_for_status()

    # 解析响应JSON数据
    json_data = response.json()

    # 从响应数据中提取嵌入向量并返回
    return [item["embedding"] for item in json_data["data"]]

  def embed_query(self, text):
    """
    将单个查询文本转换为嵌入向量

    参数:
    text: 查询文本

    返回:
    对应的嵌入向量
    """
    # 调用embed_documents处理单个文本，并返回第一个结果
    return self.embed_documents([text])[0]
