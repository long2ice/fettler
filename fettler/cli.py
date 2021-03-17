import asyncio
import socket
import sys
from functools import wraps

import click
from click import Context
from dynaconf import Dynaconf

from fettler import __VERSION__, consumer, producer


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f(*args, **kwargs))

    return wrapper


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__VERSION__, "-v", "--version")
@click.option("-c", "--config", show_default=True, default="./config.yml", help="Config file.")
@click.pass_context
def cli(ctx: Context, config: str):
    ctx.ensure_object(dict)
    settings = Dynaconf(
        settings_files=[config],
    )
    ctx.obj["settings"] = settings


@cli.command(help="Start consumer.")
@click.option(
    "-n",
    "--name",
    show_default=True,
    default=socket.gethostname(),
    help="Consumer name, default is hostname.",
)
@click.pass_context
@coro
async def consume(ctx: Context, name: str):
    settings = ctx.obj["settings"]
    await consumer.run(settings, name)


@cli.command(help="Start producer.")
@click.pass_context
@coro
async def produce(ctx: Context):
    settings = ctx.obj["settings"]
    await producer.run(settings)


def main():
    sys.path.insert(0, ".")
    cli()


if __name__ == "__main__":
    main()
