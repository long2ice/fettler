import typer

app = typer.Typer()


@app.command()
def consumer():
    pass


@app.command()
def producer():
    pass


@app.command()
def server():
    pass


if __name__ == "__main__":
    app()
