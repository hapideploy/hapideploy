import os
import typing

import yaml

from ..exceptions import InvalidHostsDefinition, InvalidProviderClass
from .deployer import Deployer


class Program(Deployer):
    def __init__(self):
        super().__init__()

        self.__discovered = []

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

                remote = self.define_remote(**data)

                if isinstance(bindings, dict):
                    for k, v in bindings.items():
                        remote.put(k, v)

    def remote(self, **kwargs):
        return super().define_remote(**kwargs)

    def group(self, name: str, desc: str, do: list[str]):
        return self.define_group(name, desc, do)

    def before(self, name: str, do):
        return super().define_hook("before", name, do)

    def after(self, name: str, do):
        return super().define_hook("after", name, do)

    def fail(self, name: str, do):
        return super().define_hook("failed", name, do)

    def resolve(self, key: str):
        return super().resolve(key)

    def task(self, name: str, desc: str):
        def wrapper(func: typing.Callable):
            self.define_task(name, desc, func)

        return wrapper


class Provider:
    def __init__(self, app: Program):
        self.app = app

    def register(self):
        raise NotImplemented
