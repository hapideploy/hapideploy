import typing

import yaml

from ..__version import __version__
from ..exceptions import RuntimeException
from .deployer import Deployer
from .remote import Remote


class Program(Deployer):
    def __init__(self):
        super().__init__()

        self.add_about_command()

    def add_about_command(self):
        @self.typer.command(name="about", help=f"Display this program information")
        def about():
            print(f"HapiDeploy {__version__}")

    def start(self):
        # TODO: If there are no remotes, try to load from inventory.yml file
        self.typer()

    def host(self, **kwargs):
        kwargs["host"] = kwargs.get("name")
        del kwargs["name"]
        remote = Remote(**kwargs)
        self.remotes.append(remote)
        return self

    def load(self, file: str = "inventory.yml"):
        with open(file) as stream:
            try:
                loaded_data = yaml.safe_load(stream)

                if isinstance(loaded_data.get("hosts"), dict) is False:
                    raise RuntimeException(f'"hosts" definition is invalid.')

                for name, data in loaded_data["hosts"].items():
                    self.host(name=name, **data)
            except yaml.YAMLError as exc:
                # TODO: throw RuntimeException
                print(exc)

    def task(self, name: str, desc: str = None):
        desc = desc if desc is not None else name

        def caller(func: typing.Callable):
            self.add_task(name, desc, func)

            def wrapper(*args, **kwargs):
                # Do something before the function call
                print("Before the function call")

                # Call the original function
                result = func(*args, **kwargs)

                # Do something after the function call
                print("After the function call")
                return result

            return wrapper

        return caller
