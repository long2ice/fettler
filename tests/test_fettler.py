import asyncio

import pytest

from conftest import TEST_KEY, get_redis
from examples.main import Test, cache


@pytest.mark.asyncio
async def test_no_filter():
    redis = get_redis()
    data = await cache(redis, TEST_KEY)
    assert data == [{"id": 1, "name": "Test"}]

    test = await Test.all().first()
    test.name = "test"
    await test.save(update_fields=["name"])
    await asyncio.sleep(2)
    data = await cache(redis, TEST_KEY)
    assert data == [{"id": 1, "name": "test"}]
