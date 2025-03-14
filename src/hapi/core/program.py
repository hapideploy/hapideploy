import os

from ..__version import __version__
from .deployer import Deployer


class Program(Deployer):
    def __init__(self):
        super().__init__()

        self.add_about_command()

    def add_about_command(self):
        @self.typer.command(name="about", help=f"Display this program information")
        def about():
            print(f"HapiDeploy {__version__}")

    def start(self):
        inventory_file = os.getcwd() + "/inventory.yml"

        self.discover(inventory_file)

        super().start()
