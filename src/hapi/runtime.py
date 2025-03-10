import typer

from hapi import Program, __version__

app = Program()


@app.typer.command(name="about", help=f"Display program information")
def about():
    print(f"HapiDeploy {__version__}")


@app.typer.command(name="list", help=f"List commands")
def list():
    print("List commands")
