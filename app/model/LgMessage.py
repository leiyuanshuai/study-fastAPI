from sqlmodel import Field
from sqlalchemy import Text, Column
from app.model.BasicModel import BasicModel
from app.utils.create_module_service import create_model_service


class LgMessage(BasicModel, table=True):
  __tablename__ = "lg_message"

  title: str = Field(default=None, description="消息标题")
  status: str = Field(default=None, description="消息的状态")
  content: str = Field(default=None, description="消息内容", sa_column=Column("content", Text, nullable=True))
  render_configs: str = Field(default=None, description="渲染配置", sa_column=Column("render_configs", Text, nullable=True))


LgMessageService = create_model_service(LgMessage)
