import asyncio
import sys
from functools import wraps

import click
import uvicorn
from click import Context
from dynaconf import Dynaconf

from fettler import __VERSION__, consumer, producer
from fettler.server import app


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f(*args, **kwargs))

    return wrapper


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__VERSION__, "-v", "--version")
@click.option("-c", "--config", default="./config.yml", help="Config file.")
@click.pass_context
def cli(ctx: Context, config: str):
    ctx.ensure_object(dict)
    settings = Dynaconf(
        settings_files=[config],
    )
    ctx.obj["settings"] = settings


@cli.command(help="Start consumer.")
@click.pass_context
@coro
async def consume(ctx: Context):
    settings = ctx.obj["settings"]
    await consumer.run(settings)


@cli.command(help="Start producer.")
@click.pass_context
@coro
async def produce(ctx: Context):
    settings = ctx.obj["settings"]
    await producer.run(settings)


@cli.command(help="Start api server.")
@click.pass_context
def serve(ctx: Context):
    settings = ctx.obj["settings"]
    server_config = settings.server
    uvicorn.run(app, debug=server_config.debug, host=server_config.host, port=server_config.port)


def main():
    sys.path.insert(0, ".")
    cli()


if __name__ == "__main__":
    main()
