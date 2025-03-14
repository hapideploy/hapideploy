import datetime

from .logger import Logger


class BufferStyle(Logger):
    def __init__(self):
        super().__init__()

        self.buffered = ""

    def write(self, level: str, message: str, context: dict = None):
        moment = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.buffered += f"[{moment}] {message}\n"

    def fetch(self) -> str:
        fetched = self.buffered
        self.buffered = ""
        return fetched
