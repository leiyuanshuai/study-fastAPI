# models.py
from datetime import datetime
from typing import Optional, List
import uuid

from sqlmodel import Field, Relationship, Column
from sqlalchemy import String

from app.model.BasicModel import BasicModel,current_datetime
# -------------------------------
# 中间表：用户-角色关联（使用 UUID 外键）
# -------------------------------
class UserRolesLink(BasicModel, table=True):
    __tablename__ = "user_roles"

    user_id: str = Field(
        default=None,
        max_length=255,
        foreign_key="user.id",
        primary_key=True,
        # sa_column=Column("user_id", String(100), nullable=False, primary_key=True)
    )
    role_id: str = Field(default=None, foreign_key="role.id", primary_key=True)

# -------------------------------
# 角色表（保持 int 自增主键，也可改为 UUID，这里保留简单性）
# -------------------------------
class Role(BasicModel, table=True):
    __tablename__ = "role"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length = 255)
    name: str = Field(..., unique=True, max_length=255, description="角色名称")
    description: str | None = Field(default=None, max_length=255)
    # 反向关系
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRolesLink)


# -------------------------------
# 用户表（id 改为 UUID）
# -------------------------------
class User(BasicModel, table=True):
    __tablename__ = "user"

    # 使用 UUID 作为主键
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),  # 自动生成 UUID
        primary_key=True,
        max_length = 255,
        index=True,
    )

    username: str = Field(...,sa_column=Column("username", String(100), unique=True, nullable=False))
    email: str= Field(sa_column=Column("email", String(255), unique=True, nullable=False), description="电子邮箱")
    password_hash: str = Field(sa_column=Column("password_hash", String(150),nullable=False), description="密码哈希")
    avatar: str | None = Field(default=None, max_length=255, description="头像URL")

    status: str | None = Field(default="inactive", regex="^(active|inactive)$", description="用户状态")

    last_login_at: datetime = Field(default_factory=current_datetime, description="最后登录时间")
    last_login_ip: str | None = Field(default=None, max_length=100, description="最后登录IP")
    # role_ids: list[str] | None = Field(default=None, description="用户的角色列表")
    # 多对多关系
    roles: List[Role] = Relationship(back_populates="users", link_model=UserRolesLink)
