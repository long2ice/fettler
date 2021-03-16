import pytest

from conftest import TEST_KEY, get_redis
from examples.main import Event, cache_test


@pytest.mark.asyncio
async def test_fettler():
    redis = get_redis()
    data = await cache_test(redis, TEST_KEY)
    assert data == [{"id": 1, "name": "Test"}]

    test = await Event.all().first()
    test.name = "test"
    await test.save(update_fields=["name"])

    data = await cache_test(redis, TEST_KEY)
    assert data == [{"id": 1, "name": "test"}]
