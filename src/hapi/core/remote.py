from typing import Callable

from fabric import Connection

from ..collect import Collection
from ..exceptions import ItemNotFound, RemoteNotFound
from .container import Container


class Remote(Container):
    def __init__(
        self,
        host: str,
        user: str | None = None,
        port: int | None = None,
        identity_file: str | None = None,
        label: str | None = None,
    ):
        super().__init__()

        self.host = host
        self.user = user
        self.port = port
        self.identity_file = identity_file
        self.label = host if label is None else label

        key = self.host

        if user:
            key = f"{user}@{key}"

        if port:
            key = f"{key}:{port}"

        self.key = key

    def connect(self) -> Connection:
        connect_kwargs = dict()
        if self.identity_file:
            connect_kwargs["key_filename"] = self.identity_file
        return Connection(
            host=self.host,
            user=self.user,
            port=self.port,
            connect_kwargs=connect_kwargs,
        )


class RemoteBag(Collection):
    SELECTOR_ALL = "all"

    def __init__(self):
        super().__init__(Remote)

        self.find_using(lambda key, remote: remote.key == key)

    def add(self, remote: Remote):
        return super().add(remote)

    def find(self, key: str) -> Remote:
        try:
            return super().find(key)
        except ItemNotFound:
            raise RemoteNotFound(f"Remote {key} was not found.")

    def match(self, callback: Callable[[Remote], bool]) -> Remote:
        try:
            return super().match(callback)
        except:
            raise RemoteNotFound("No remotes match the given callback.")

    def filter(self, callback: Callable[[Remote], bool]) -> list[Remote]:
        return super().filter(callback)

    def all(self) -> list[Remote]:
        return super().all()

    def select(self, selector: str) -> list[Remote]:
        if selector == self.SELECTOR_ALL:
            return self.all()
        return self.filter(lambda remote: remote.label == selector)
