import re
import shlex
import typing

from .exceptions import ItemNotFound


def env_stringify(env: dict) -> str:
    items = []
    for name, value in env.items():
        items.append(f"%s=%s" % (name, shlex.quote(str(value))))
    return " ".join(items)


def extract_curly_brackets(text):
    pattern = r"\{\{([^}]*)\}\}"
    matches = re.findall(pattern, text)
    return matches


class Collection:
    def __init__(self, cls):
        self.__cls = cls
        self.__items = []
        self.__filter_key = lambda key, item: False

    def add(self, item):
        if not isinstance(item, self.__cls):
            raise TypeError(f"item must be an instance of {self.__cls.__name__}.")

        self.__items.append(item)

    def empty(self) -> bool:
        return len(self.__items) == 0

    def find(self, key: str):
        for item in self.__items:
            if self.__filter_key(key, item):
                return item

        raise ItemNotFound(f"Item with {key} is not found in the collection.")

    def match(self, callback: typing.Callable):
        for item in self.__items:
            if callback(item):
                return item

        raise ItemNotFound(f"Item is not found in the collection.")

    def filter(self, callback: typing.Callable) -> list:
        return [item for item in self.__items if callback(item)]

    def all(self):
        return self.__items

    def filter_key(self, callback: typing.Callable):
        self.__filter_key = callback
