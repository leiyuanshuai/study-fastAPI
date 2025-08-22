import asyncio
import sys
from typing import Optional, Annotated
import redis.asyncio as redis
from fastapi import Depends
from app.config.env import env


class RedisManager:
    _instance: Optional[redis.Redis] = None
    _lock = asyncio.Lock()

    @staticmethod
    async def get_instance() -> redis.Redis:
        async with RedisManager._lock:
            if RedisManager._instance is None:
                RedisManager._instance = redis.Redis(
                    host=env.redis_db_host,
                    port=env.redis_db_port,
                    password=env.redis_db_password or None,
                    db=int(env.redis_db_number),
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30,
                    retry_on_timeout=True,
                    max_connections=20
                )
                
                # 测试连接
                try:
                    await RedisManager._instance.ping()
                    print("✅ Redis连接成功")
                except Exception as e:
                    print(f"❌ Redis连接失败: {e}")
                    raise e
                    
        return RedisManager._instance

    @staticmethod
    async def close_instance():
        async with RedisManager._lock:
            if RedisManager._instance is not None:
                await RedisManager._instance.close()
                RedisManager._instance = None
                print("✅ Redis连接已关闭")


# 定义依赖注入类型
RedisDep = Annotated[redis.Redis, Depends(RedisManager.get_instance)]


async def check_redis_connection():
    """用于启动服务的时候检查Redis连接是否正常"""
    try:
        redis_client = await RedisManager.get_instance()
        await redis_client.ping()
        print("✅ Redis连接检查成功")
    except Exception as e:
        print(f"❌ Redis连接检查失败: {e}")
        raise e