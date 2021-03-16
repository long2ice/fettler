import asyncio
import json

import aioredis
import httpx
from aioredis import Redis
from tortoise import Tortoise, fields, run_async
from tortoise.models import Model


class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    class Meta:
        table = "test"


async def register_policy(key: str):
    async with httpx.AsyncClient() as client:
        data = {
            "schema": "test",
            "table": "test",
            "key": key,
        }
        await client.post("http://127.0.0.1:8000/policy", json=data)


async def cache_test(redis: Redis, key: str):
    data = await redis.get(key)
    if not data:
        data = await Event.all().values("id", "name")
        await redis.set(key, json.dumps(data))
        await register_policy(key)
    else:
        data = json.loads(data)
    return data


async def run():
    await Tortoise.init(
        db_url="mysql://root:123456@127.0.0.1:3306/test", modules={"models": ["__main__"]}
    )
    await Tortoise.generate_schemas()
    redis = await aioredis.create_redis_pool("redis://127.0.0.1:6379", db=0, encoding="utf8")
    key = "test_cache"
    await redis.delete(key)
    await Tortoise.get_connection("default").execute_query("truncate table test")
    test = await Event.create(name="Test")

    data = await cache_test(redis, key)
    assert data == [{"id": 1, "name": "Test"}]

    test.name = "test"
    await test.save(update_fields=["name"])

    await asyncio.sleep(2)
    # cache will auto delete by fettler, so we will get new data
    data = await cache_test(redis, key)
    assert data == [{"id": 1, "name": "test"}]

    await Tortoise.close_connections()
    redis.close()
    await redis.wait_closed()


if __name__ == "__main__":
    run_async(run())
