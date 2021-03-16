import json

import aioredis
from aioredis import errors
from dynaconf import Dynaconf
from loguru import logger

from fettler import constants
from fettler.utils import is_match_filters, object_hook


async def run(settings: Dynaconf, name: str):
    redis = settings.redis
    redis = await aioredis.create_redis_pool(
        f"redis://{redis.host}:{redis.port}", db=redis.db, encoding="utf8"
    )
    try:
        await redis.xgroup_create(constants.STREAM, constants.GROUP_NAME, mkstream=True)
    except errors.BusyGroupError:
        pass
    logger.info("Start consumer success")
    while True:
        msgs = await redis.xread_group(
            constants.GROUP_NAME, name, [constants.STREAM], latest_ids=[">"]
        )
        for msg_item in msgs:
            stream, msg_id, raw_msg = msg_item
            data = json.loads(raw_msg.get("msg"), object_hook=object_hook)
            schema = data.get("schema")
            table = data.get("table")
            type_ = data.get("type")
            rows = data.get("rows")
            if type_ in ["create", "delete"]:
                values = rows[0]["values"]
            else:
                values = rows[0]["after_values"]
            key = f"{constants.PREFIX}{schema}:{table}"
            data = await redis.hgetall(key)
            delete_keys = []
            for k, v in data.items():
                filters = json.loads(v, object_hook=object_hook)
                if filters:
                    if is_match_filters(values, filters):
                        delete_keys.append(k)
                else:
                    delete_keys.append(k)
            if delete_keys:
                await redis.delete(*delete_keys)
                logger.info(f"Delete keys {delete_keys} from {schema}.{table}")
