from typing import Any


class Logger:
    LEVEL_DEBUG = "DEBUG"

    def debug(self, message: str, context: dict[Any, Any] | None = None):
        self.write(level=Logger.LEVEL_DEBUG, message=message, context=context)

    def write(self, level: str, message: str, context: dict[Any, Any] | None = None):
        raise NotImplementedError
