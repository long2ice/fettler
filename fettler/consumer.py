import json

import aioredis
from aioredis import errors
from dynaconf import Dynaconf

from fettler import constants
from fettler.utils import object_hook


async def run(settings: Dynaconf, name: str):
    redis = settings.redis
    redis = await aioredis.create_redis_pool(
        f"redis://{redis.host}:{redis.port}", db=redis.store_db, encoding="utf8"
    )
    try:
        await redis.xgroup_create(constants.STREAM, constants.GROUP_NAME)
    except errors.BusyGroupError:
        pass
    while True:
        msgs = await redis.xread_group(
            constants.GROUP_NAME, name, [constants.STREAM], latest_ids=[">"]
        )
        for msg_item in msgs:
            stream, msg_id, raw_msg = msg_item
            data = json.loads(raw_msg.get("msg"), object_hook=object_hook)
            print(data)
