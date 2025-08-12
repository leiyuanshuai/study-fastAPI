import asyncio
import sys
from contextlib import asynccontextmanager
from typing import Annotated, AsyncContextManager
from fastapi.params import Depends
from sqlalchemy import AsyncAdaptedQueuePool, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# from app.model.user_role import User, Role, UserRolesLink  # 必须导入模型

from app.config.env import env
from sqlmodel import create_engine
# from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = f"mysql+asyncmy://{env.db_username}:{env.db_password}@{env.db_host}:{env.db_port}/{env.db_database}?charset=utf8mb4"

# 创建异步引擎实例，用于异步操作数据库
async_engine = AsyncEngine(create_engine(
  DATABASE_URL,
  poolclass=AsyncAdaptedQueuePool,  # 使用异步适配的队列池
  pool_size=5,  # 连接池保持的连接数
  max_overflow=10,  # 允许超过pool_size的最大连接数
  pool_timeout=30,  # 获取连接的超时时间(秒)
  pool_recycle=3600,  # 连接回收时间(秒)
  echo=True,  # 启用SQL语句日志输出，便于开发调试
  future=True,  # 启用SQLAlchemy 2.0风格的未来模式API
))

# 创建一个会话工厂函数
async_session = sessionmaker(
  bind=async_engine,
  class_=AsyncSession,
  expire_on_commit=False
)

# 作用：用于在接口中注入得到会话实例对象session，在接口执行完毕之后，自动执行close动作关闭会话
async def get_async_session() -> AsyncSession:
  async with async_session() as session:
    yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


# 用于启动服务的时候检查数据库连接是否正常
async def check_database_connection():
  """检查数据库连接是否正常"""
  try:
    async with async_engine.begin() as conn:
      await conn.execute(text("select 1"))
      # 打印连接成功信息及连接URL
      print(f"✅ 数据库{env.db_database}连接成功", env.db_host, env.db_port)
      # await conn.run_sync(SQLModel.metadata.create_all)
      print("✅ 创建user,role,user_roles_link表成功")
  except Exception as e:
    # 打印连接失败信息及错误详情
    print(f"❌ Database connection failed: {e}")
    # 重新抛出异常，让上层处理
    raise e

  return async_engine

#
if sys.platform == "win32":
  from asyncio import WindowsSelectorEventLoopPolicy

  asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())  # 在Windows平台上设置事件循环策略为WindowsSelectorEventLoopPolicy

POSTGRES_DATABASE_URL = f"postgresql://{env.pg_db_username}:{env.pg_db_password}@{env.pg_db_host}:{env.pg_db_port}/{env.pg_db_database}"  # 构造PostgreSQL数据库连接字符串


async def aopen_postgres_checkpointer() -> AsyncPostgresSaver:  # 定义一个异步上下文管理器函数，返回一个AsyncPostgresSaver实例
  try:
    # 测试连接并初始化表结构
    async with AsyncPostgresSaver.from_conn_string(POSTGRES_DATABASE_URL) as checkpointer:  # 使用连接字符串创建AsyncPostgresSaver实例
      yield checkpointer  # 生成checkpointer实例供外部使用
  except Exception as e:
    print(f"[Postgres]数据库连接失败: {e}")  # 捕获异常并打印错误信息


# 用于启动服务的时候检查Postgres数据库连接是否正常
async def check_postgres_connection():
  """检查数据库连接是否正常"""
  try:
    async with AsyncPostgresSaver.from_conn_string(POSTGRES_DATABASE_URL):
      print("✅ Postgres connection successful：")
  except Exception as e:
    # 打印连接失败信息及错误详情
    print(f"❌ Postgres connection failed: {e}")
    # 重新抛出异常，让上层处理
    raise e


AsyncPostgresSaverDep = Annotated[AsyncPostgresSaver, Depends(aopen_postgres_checkpointer)]


def is_super_admin_by_role_id(role_id: str) -> bool:
    """检查是否为超级管理员角色"""
    return role_id == "da4ad6b1130944ee8ea8676f35231a9f"
