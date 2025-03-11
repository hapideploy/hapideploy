import typing

import yaml

from .deployer import Deployer
from .remote import RemoteDefinition


class Program:
    def __init__(self):
        self.deployer = Deployer()

        # TODO: Register default commands.
        @self.deployer.typer.command(name="about", help=f"Display program information")
        def about():
            print(f"HapiDeploy {__version__}")

        @self.deployer.typer.command(name="list", help=f"List commands")
        def list():
            print("List commands")

    def start(self):
        # TODO: If there are no remotes, try to load from inventory.yml file
        self.deployer.typer()

    def put(self, key: str, value):
        self.deployer.config.put(key, value)
        return self

    def add(self, key: str, value):
        self.deployer.config.add(key, value)
        return self

    def host(self, **kwargs):
        kwargs["host"] = kwargs.get("name")
        del kwargs["name"]
        remote = RemoteDefinition(**kwargs)
        self.deployer.remotes.append(remote)
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
            self.deployer.add_task(name, desc, func)

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
