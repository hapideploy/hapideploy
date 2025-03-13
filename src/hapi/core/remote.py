from fabric import Connection


class Remote:
    def __init__(
        self,
        host: str,
        user: str = "hapi",
        port: int = 22,
        deploy_dir: str = "~/deploy/{{stage}}",
        label: str = None,
    ):
        self.host = host
        self.user = user
        self.port = port
        self.deploy_dir = deploy_dir
        self.label = host if label is None else label
        self.id = f"{self.user}@{self.host}:{self.port}"

    def connect(self) -> Connection:
        return Connection(host=self.host, user=self.user, port=self.port)
