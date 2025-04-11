from typing import Any, Callable

from .exceptions import ItemNotFound


class Collection:
    def __init__(self, cls):
        self.__cls = cls
        self.__items = []
        self.__find_callback = lambda key, item: False

    def empty(self) -> bool:
        return len(self.__items) == 0

    def add(self, item: Any):
        if not isinstance(item, self.__cls):
            raise TypeError(f"item must be an instance of {self.__cls.__name__}.")

        self.__items.append(item)

    def find(self, key: str) -> Any:
        for item in self.__items:
            if self.__find_callback(key, item):
                return item

        raise ItemNotFound(f"Item with {key} is not found in the collection.")

    def match(self, callback: Callable[[Any], bool]) -> Any:
        for item in self.__items:
            if callback(item):
                return item

        raise ItemNotFound(f"Item is not found in the collection.")

    def filter(self, callback: Callable[[Any], bool]) -> list[Any]:
        return [item for item in self.__items if callback(item)]

    def all(self) -> list[Any]:
        return self.__items

    def find_using(self, callback: Callable[[int | str, Any], bool]):
        self.__find_callback = callback
