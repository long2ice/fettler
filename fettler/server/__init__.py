import json
from typing import Optional

import aioredis
from aioredis import Redis
from dynaconf import Dynaconf
from fastapi import FastAPI
from starlette.responses import JSONResponse

from fettler import constants
from fettler.server.schemas import Policy
from fettler.utils import JsonEncoder

redis: Optional[Redis] = None


def create_app(settings: Dynaconf):
    app = FastAPI()
    config = settings.redis

    @app.on_event("startup")
    async def startup():
        global redis
        redis = await aioredis.create_redis_pool(
            f"redis://{config.host}:{config.port}", db=config.db, encoding="utf8"
        )

    @app.post("/policy", summary="add cache refresh policy")
    async def add_policy(policy: Policy):
        schema = policy.database
        table = policy.table
        key = policy.key
        await redis.hset(
            f"{constants.PREFIX}{schema}:{table}", key, json.dumps(policy.filters, cls=JsonEncoder)
        )
        return JSONResponse(content=dict(code=200))

    return app
