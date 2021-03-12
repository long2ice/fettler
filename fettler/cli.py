import sys

import click
import uvicorn
from click import Context
from dynaconf import Dynaconf

from fettler import __VERSION__
from fettler.server import app


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__VERSION__, "-v", "--version")
@click.option('-c', "--config", default='./config.yml', help="Config file.")
@click.pass_context
def cli(ctx: Context, config: str):
    ctx.ensure_object(dict)
    settings = Dynaconf(
        settings_files=[config],
    )
    ctx.obj["settings"] = settings


@cli.command(help="Start consumer.")
@click.pass_context
def consumer(ctx: Context):
    settings = ctx.obj["settings"]


@cli.command(help="Start producer.")
@click.pass_context
def producer(ctx: Context):
    settings = ctx.obj["settings"]


@cli.command(help="Start api server.")
@click.pass_context
def server(ctx: Context):
    settings = ctx.obj["settings"]
    server_config = settings.server
    uvicorn.run(app, debug=server_config.debug, host=server_config.host, port=server_config.port)


def main():
    sys.path.insert(0, ".")
    cli()


if __name__ == '__main__':
    main()
