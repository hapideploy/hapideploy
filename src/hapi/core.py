"""habideploy package."""

__version__ = "0.1.0"

import typer
from fabric import Connection


class LogicException(Exception):
    pass


class Configuration:
    def __init__(self):
        self.__items = {}

    def put(self, key: str, value):
        self.__items[key] = value
        return self

    def add(self, key: str, value):
        if self.__items.get(key) is None:
            self.__items[key] = []

        if isinstance(self.__items[key], list) is False:
            raise LogicException(f'The value associated with "{key}" is not a list.')

        if isinstance(value, list):
            for v in value:
                self.__items[key].append(v)
        else:
            self.__items[key].append(value)

        return self

    def find(self, key: str):
        return self.__items.get(key)

    def all(self) -> dict:
        return self.__items


class RemoteDefinition:
    def __init__(
        self,
        host: str,
        user: str = "forge",
        deploy_dir: str = "~/deploy/{{stage}}",
        label: str = None,
    ):
        self.host = host
        self.user = user
        self.deploy_dir = deploy_dir
        self.label = host if label is None else label

    def connect(self):
        return Connection(host=self.host, user=self.user)


class Deployer:
    instance = None

    def __init__(self):
        self.config = Configuration()
        self.remotes = []

    @staticmethod
    def set_instance(instance):
        Deployer.instance = instance

    @staticmethod
    def get_instance():
        if Deployer.instance is None:
            Deployer.instance = Deployer()
        return Deployer.instance


class Program:
    def __init__(self):
        self.deployer = Deployer()
        self.typer = typer.Typer()

    def start(self):
        self.typer()

    def put(self, key: str, value):
        self.deployer.config.put(key, value)
        return self

    def add(self, key: str, value):
        self.deployer.config.add(key, value)
        return self

    def host(
        self,
        name: str,
        user: str = "forge",
        deploy_dir: str = "~/deploy/{{stage}}",
        label: str = None,
    ):
        remote = RemoteDefinition(
            host=name, user=user, deploy_dir=deploy_dir, label=label
        )
        self.deployer.remotes.append(remote)
        return self
