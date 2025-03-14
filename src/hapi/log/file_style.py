import datetime

from .logger import Logger


class FileStyle(Logger):
    def __init__(self, file: str):
        super().__init__()
        self.__channel = "Hapi"
        self.__file = file

    def write(self, level: str, message: str, context: dict = None):
        moment = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(self.__file, "a") as stream:
            stream.write(f"[{moment}] {message}\n")
