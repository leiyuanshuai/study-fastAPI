from typing import Annotated
from fastapi.params import Depends
from sqlalchemy import AsyncAdaptedQueuePool, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.env import env
from sqlmodel import create_engine
# from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = f"mysql+asyncmy://{env.db_username}:{env.db_password}@{env.db_host}:{env.db_port}/{env.db_database}?charset=utf8mb4"

# 创建异步引擎实例，用于异步操作数据库
async_engine = AsyncEngine(create_engine(
  DATABASE_URL,
  poolclass=AsyncAdaptedQueuePool,  # 使用异步适配的队列池
  pool_size=10,  # 连接池保持的连接数
  max_overflow=20,  # 允许超过pool_size的最大连接数
  pool_timeout=60,  # 获取连接的超时时间(秒)
  pool_recycle=300,  # 连接回收时间(秒)
  pool_pre_ping=True,  # 预检查连接是否可用，防止连接断开
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

def is_super_admin_by_role_id(role_id: str) -> bool:
    """检查是否为超级管理员角色"""
    return role_id == "da4ad6b1130944ee8ea8676f35231a9f"
