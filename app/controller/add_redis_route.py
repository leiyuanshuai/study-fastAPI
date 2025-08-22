from fastapi import FastAPI, APIRouter
from app.utils.redis_utils import RedisDep
import time


def add_redis_route(app: FastAPI, prefix):
    router = APIRouter(prefix=prefix, tags=["测试redis"])

    @router.get("/test")
    async def redis_test(redis_client: RedisDep):
        """Redis测试接口"""
        try:
            # 测试基本的key-value操作
            test_key = "test_key"
            test_value = f"Hello Redis! {int(time.time())}"

            # 设置键值
            await redis_client.set(test_key, test_value, ex=300)  # 5分钟过期

            # 获取键值
            retrieved_value = await redis_client.get(test_key)

            # 测试列表操作
            list_key = "test_list"
            await redis_client.lpush(list_key, "item1", "item2", "item3")
            list_items = await redis_client.lrange(list_key, 0, -1)

            # 测试哈希操作
            hash_key = "test_hash"
            await redis_client.hset(hash_key, mapping={
                "field1": "value1",
                "field2": "value2",
                "timestamp": str(int(time.time()))
            })
            hash_data = await redis_client.hgetall(hash_key)

            # 测试集合操作
            set_key = "test_set"
            await redis_client.sadd(set_key, "member1", "member2", "member3")
            set_members = await redis_client.smembers(set_key)

            # 获取Redis信息
            info = await redis_client.info()

            return {
                "success": True,
                "data": {
                    "basic_test": {
                        "set_key": test_key,
                        "set_value": test_value,
                        "retrieved_value": retrieved_value
                    },
                    "list_test": {
                        "key": list_key,
                        "items": list_items
                    },
                    "hash_test": {
                        "key": hash_key,
                        "data": hash_data
                    },
                    "set_test": {
                        "key": set_key,
                        "members": list(set_members)
                    },
                    "redis_info": {
                        "redis_version": info.get("redis_version"),
                        "connected_clients": info.get("connected_clients"),
                        "used_memory_human": info.get("used_memory_human"),
                        "uptime_in_seconds": info.get("uptime_in_seconds")
                    }
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @router.post("/set")
    async def redis_set(key: str, value: str, expire: int = 300, redis_client: RedisDep = None):
        """设置Redis键值"""
        try:
            await redis_client.set(key, value, ex=expire)
            return {"success": True, "message": f"键 {key} 已设置"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @router.get("/get/{key}")
    async def redis_get(key: str, redis_client: RedisDep = None):
        """获取Redis键值"""
        try:
            value = await redis_client.get(key)
            if value is None:
                return {"success": False, "message": f"键 {key} 不存在"}
            return {"success": True, "key": key, "value": value}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @router.delete("/delete/{key}")
    async def redis_delete(key: str, redis_client: RedisDep = None):
        """删除Redis键"""
        try:
            result = await redis_client.delete(key)
            if result:
                return {"success": True, "message": f"键 {key} 已删除"}
            else:
                return {"success": False, "message": f"键 {key} 不存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    app.include_router(router)
