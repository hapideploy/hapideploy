from fabric import Connection

from .container import Container


class Remote(Container):
    def __init__(
        self,
        host: str,
        user: str = "hapi",
        port: int = 22,
        deploy_dir: str = "~/deploy/{{stage}}",
        label: str = None,
        pemfile: str = None,
    ):
        super().__init__()

        self.host = host
        self.user = user
        self.port = port
        self.deploy_dir = deploy_dir
        self.label = host if label is None else label
        self.id = f"{self.user}@{self.host}:{self.port}"
        self.pemfile = pemfile

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
