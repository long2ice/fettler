import asyncio
import json

import aioredis
from aioredis import Redis
from tortoise import Tortoise, fields, run_async
from tortoise.models import Model

from fettler import constants
from fettler.utils import JsonEncoder


class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    class Meta:
        table = "test"


async def cache(redis: Redis, key: str, filters=None):
    if filters is None:
        filters = {}
    data = await redis.get(key)
    if not data:
        data = await Event.all().values("id", "name")
        p = redis.pipeline()
        p.set(key, json.dumps(data))
        # set cache invalid policy, the hset name format is fettler:<schema>:<table>, key is cache key, and value is filters
        p.hset(f"{constants.PREFIX}test:test", key, json.dumps(filters, cls=JsonEncoder))
        await p.execute()
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

    data = await cache(redis, key)
    assert data == [{"id": 1, "name": "Test"}]

    test.name = "test"
    await test.save(update_fields=["name"])

    await asyncio.sleep(2)
    # old cache will auto delete by fettler, so we will get latest data
    data = await cache(redis, key)
    assert data == [{"id": 1, "name": "test"}]

    await Tortoise.close_connections()
    redis.close()
    await redis.wait_closed()


if __name__ == "__main__":
    run_async(run())
