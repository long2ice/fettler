import json

import aioredis
from asyncmy import connect
from asyncmy.replication.binlogstream import BinLogStream
from asyncmy.replication.row_events import DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent
from dynaconf import Dynaconf
from loguru import logger

from fettler import constants
from fettler.utils import JsonEncoder


async def run(settings: Dynaconf):
    mysql = settings.mysql
    redis = settings.redis
    max_len = redis.max_len or constants.STREAM_MAX_LEN
    redis = await aioredis.create_redis_pool(
        f"redis://{redis.host}:{redis.port}", db=redis.db, encoding="utf8"
    )
    connect_kwargs = dict(
        host=mysql.host, port=mysql.port, user=mysql.user, password=mysql.password
    )
    conn = await connect(**connect_kwargs)
    ctl_conn = await connect(**connect_kwargs)
    stream = BinLogStream(
        connection=conn,
        ctl_connection=ctl_conn,
        resume_stream=True,
        blocking=True,
        only_events=[WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent],
        **settings.replication,
    )
    await stream.connect()
    logger.info("Start producer success, listening on binlog....")
    async for event in stream:
        if isinstance(event, DeleteRowsEvent):
            type_ = "delete"
        elif isinstance(event, WriteRowsEvent):
            type_ = "create"
        else:
            type_ = "update"
        msg = {"schema": event.schema, "table": event.table, "rows": event.rows, "type": type_}
        msg = json.dumps(msg, cls=JsonEncoder)
        await redis.xadd(constants.STREAM, {"msg": msg}, max_len=max_len)
