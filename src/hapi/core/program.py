import os
import typing

import yaml

from ..__version import __version__
from ..exceptions import InvalidHostsDefinition, InvalidProviderClass
from .deployer import Deployer


class Program(Deployer):
    def __init__(self):
        super().__init__()

        self.__discovered = []

        self.add_about_command()
        self.command_task_list()

    def add_about_command(self):
        def about(_):
            print(f"HapiDeploy {__version__}")

        self.add_command("about", "Display this program information", about)

    def command_task_list(self):
        def task_list(dep: Deployer):
            tasks = dep.tasks().all()

            for task in tasks:
                dep.io().writeln(f"<primary>{task.name}</primary>  {task.desc}")

        self.add_command("task:list", "List tasks", task_list)

    def start(self):
        inventory_file = os.getcwd() + "/inventory.yml"

        self.discover(inventory_file)

        super().start()

    def load(self, cls):
        if not issubclass(cls, Provider):
            raise InvalidProviderClass("The given class must be a subclass of Provider")
        provider = cls(self)
        provider.register()

    def discover(self, file: str = "inventory.yml"):
        if file in self.__discovered:
            return

        with open(file) as stream:
            self.__discovered.append(file)

            loaded_data = yaml.safe_load(stream)

            if (
                loaded_data is None
                or isinstance(loaded_data.get("hosts"), dict) is False
            ):
                raise InvalidHostsDefinition(f'"hosts" definition is invalid.')

            for key, data in loaded_data["hosts"].items():
                if data.get("host") is None:
                    data["host"] = key
                else:
                    data["label"] = key

                bindings = data.get("with")

                if bindings is not None:
                    del data["with"]

                remote = self.add_remote(**data)

                if isinstance(bindings, dict):
                    for k, v in bindings.items():
                        remote.put(k, v)

    def remote(self, **kwargs):
        return super().add_remote(**kwargs)

    def put(self, key: str, value):
        return super().put(key, value)

    def add(self, key: str, value):
        return super().add(key, value)

    def make(self, key: str, fallback=None, throw=None):
        return super().make(key, fallback, throw)

    def parse(self, text: str, **kwargs) -> str:
        return super().parse(text, **kwargs)

    def resolve(self, key: str):
        return super().resolve(key)

    def command(self, name: str, desc: str):
        def caller(func: typing.Callable):
            self.add_command(name, desc, func)

        return caller

    def task(self, name: str, desc: str):
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

    def group(self, name: str, desc: str, do: list[str]):
        return self.add_group(name, desc, do)


class Provider:
    def __init__(self, app: Program):
        self.app = app

    def register(self):
        raise NotImplemented
