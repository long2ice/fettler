import typer
from dynaconf import settings

app = typer.Typer()

config_option = typer.Option('./config.yml', "-c", "--config", help='Config file.')


@app.command()
def consumer(config: str = config_option):
    settings.load_file(config)


@app.command()
def producer(config: str = config_option):
    settings.load_file(config)


@app.command()
def server(config: str = config_option):
    settings.load_file(config, env='')
    print(settings.items())


if __name__ == "__main__":
    app()
