from asyncmy import connect
from asyncmy.replication.binlogstream import BinLogStream
from asyncmy.replication.row_events import DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent
from dynaconf import Dynaconf


async def run(settings: Dynaconf):
    mysql = settings.mysql
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
    async for event in stream:
        print(event)
