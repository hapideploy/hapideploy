import typer

from hapi import Deployer, Program, __version__

app = Program()


@app.deployer.typer.command(name="about", help=f"Display program information")
def about():
    print(f"HapiDeploy {__version__}")


@app.deployer.typer.command(name="list", help=f"List commands")
def list():
    print("List commands")


@app.task(name="deploy:start", desc="Start a new deployment")
def deploy_start(dep: Deployer):
    release_name = (
        dep.cat("{{deply_dir}}/.dep/latest_release")
        if dep.test("{{deply_dir}}/.dep/latest_release")
        else 1
    )

    # print(f'release_name {release_name}')
