import typing

from fabric import Connection

from ..exceptions import ItemNotFound, RemoteNotFound
from ..support import Collection
from .container import Container


class Remote(Container):
    def __init__(
        self,
        host: str,
        user: str = "hapi",
        port: int = 22,
        label: str = None,
        pemfile: str = None,
    ):
        super().__init__()

        self.host = host
        self.user = user
        self.port = port
        self.label = host if label is None else label
        self.pemfile = pemfile
        self.key = f"{self.user}@{self.host}:{self.port}"

    def connect(self) -> Connection:
        connect_kwargs = dict()
        if self.pemfile:
            connect_kwargs["key_filename"] = self.pemfile
        return Connection(
            host=self.host,
            user=self.user,
            port=self.port,
            connect_kwargs=connect_kwargs,
        )


class RemoteBag(Collection):
    def __init__(self):
        super().__init__(Remote)

        self.filter_key(lambda key, remote: remote.key == key)

    def add(self, remote: Remote):
        return super().add(remote)

    def find(self, name: str) -> Remote:
        try:
            return super().find(name)
        except ItemNotFound:
            raise RemoteNotFound(f"remote {name} is not found.")

    def match(self, callback: typing.Callable) -> Remote:
        try:
            return super().match(callback)
        except:
            raise RemoteNotFound

    def filter(self, callback: typing.Callable) -> list[Remote]:
        return super().filter(callback)

    def all(self) -> list[Remote]:
        return super().all()
