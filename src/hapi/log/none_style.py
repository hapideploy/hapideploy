from typing import Any

from .logger import Logger


class NoneStyle(Logger):
    def write(self, level: str, message: str, context: dict[Any, Any] | None = None):
        pass
