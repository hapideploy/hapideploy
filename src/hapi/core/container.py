import re
import typing

from ..exceptions import BindingException, LogicException


class Container:
    __instance = None

    def __init__(self):
        self.__bindings = {}
        self.__items = {}

    @staticmethod
    def set_instance(instance):
        Container.__instance = instance

    @staticmethod
    def get_instance():
        if Container.__instance is None:
            Container.__instance = Container()
        return Container.__instance

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
        return key in self.__bindings or key in self.__items

    def bind(self, key: str, callback: typing.Callable):
        self.__bindings[key] = callback

    def make(self, key: str):
        if key in self.__bindings:
            return self.__bindings[key](self)
        return self.__items.get(key)

    def parse(self, text: str, params: dict = None):
        keys = self._extract_curly_braces(text)

        for key in keys:
            if params is not None and key in params:
                text = text.replace("{{" + key + "}}", str(params[key]))
                continue

            if self.has(key) is not True:
                raise BindingException(
                    f'The key "{key}" is not defined in the container.'
                )

            value = self.make(key)

            if value is not None:
                text = text.replace("{{" + key + "}}", str(value))

        return text

    @staticmethod
    def _extract_curly_braces(text):
        pattern = r"\{\{([^}]*)\}\}"
        matches = re.findall(pattern, text)
        return matches
