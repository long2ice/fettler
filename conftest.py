import asyncio
from typing import Optional

import aioredis
import pytest
from aioredis import Redis
from tortoise import Tortoise

from examples import main
from examples.main import Event

TEST_KEY = "test_cache"
redis: Optional[Redis] = None


def get_redis():
    return redis


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    res = policy.new_event_loop()
    asyncio.set_event_loop(res)
    res._close = res.close
    res.close = lambda: None

    yield res

    res._close()


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    global redis
    await Tortoise.init(
        db_url="mysql://root:123456@127.0.0.1:3306/test", modules={"models": [main]}
    )
    await Tortoise.generate_schemas()
    redis = await aioredis.create_redis_pool("redis://127.0.0.1:6379", db=0, encoding="utf8")
    await redis.delete(TEST_KEY)
    await Tortoise.get_connection("default").execute_query("truncate table test")
    await Event.create(name="Test")
