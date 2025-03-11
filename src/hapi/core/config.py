import typing

from ..exceptions import LogicException


class Configuration:
    def __init__(self):
        self.__items = {}

    def put(self, key: str, value):
        self.__items[key] = value
        return self

    def add(self, key: str, value):
        if self.__items.get(key) is None:
            self.__items[key] = []

        if isinstance(self.__items[key], list) is False:
            raise LogicException(f'The value associated with "{key}" is not a list.')

        if isinstance(value, list):
            for v in value:
                self.__items[key].append(v)
        else:
            self.__items[key].append(value)

        return self

    def has(self, key: str):
        return key in self.__items

    def find(self, key: str):
        return self.__items.get(key)

    def all(self) -> dict:
        return self.__items
