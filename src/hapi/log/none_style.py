from .logger import Logger


class NoneStyle(Logger):
    def write(self, level: str, message: str, context: dict = None):
        pass
