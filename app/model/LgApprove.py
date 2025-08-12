from sqlmodel import Field
from sqlalchemy import Text, Column
from app.model.BasicModel import BasicModel
from app.utils.create_module_service import create_model_service


class LgApprove(BasicModel, table=True):
  __tablename__ = "lg_approve"

  status: str = Field(default=None, description="报销单的状态")
  remarks: str = Field(default=None, description="报销备注信息", sa_column=Column("remarks", Text, nullable=True))
  result_content: str = Field(default=None, description="审批结果信息", sa_column=Column("result_content", Text, nullable=True))


LgApproveService = create_model_service(LgApprove)
