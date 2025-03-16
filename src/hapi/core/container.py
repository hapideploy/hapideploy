import typing

from ..exceptions import BindingException, LogicException
from ..support import extract_curly_braces


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
        """
        Put a value with its associated key in the container.

        :param str key: The unified key (identifier) in the container.
        :param value: The value is associated with the given key.
        """
        self.__items[key] = value
        return self

    def add(self, key: str, value):
        """
        Append one or more values to the given key in the container.

        :param str key: The unified key (identifier) in the container.
        :param value: It can be a single value such as int, str or a list.
        """
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

    def bind(self, key: str, callback: typing.Callable):
        """
        Bind a callback to its key in the container.
        """
        self.__bindings[key] = callback
        return self

    def resolve(self, key: str):
        """
        Bind a callback to its key in the container using decorator.

            @container.resolve
            def resolve_tools(_)
                return ['poetry', 'typer', 'fabric']

        :param str key: The unified key (identifier) in the container.
        """

        def caller(func: typing.Callable):
            self.bind(key, func)

        return caller

    def has(self, key: str):
        """
        Determine if the given key exists in the container.

        :param str key: The key (identifier) needs to be checked.
        """
        return key in self.__bindings or key in self.__items

    def make(self, key: str, fallback: any = None, throw=None):
        """
        Resolve an item from the container.

        :param str key: The key (identifier) needs to be resolved.
        :param any fallback: This will be returned if key does not exist.
        :param bool|Exception throw: Determine if it should raise an exception if key does not exist.
        """
        if not self.has(key):
            if throw is None or throw is False:
                return fallback

            if throw is True:
                raise BindingException.with_key(key)

            if isinstance(throw, Exception):
                raise throw

            raise LogicException(
                f"throw must be either None, bool or an instance of Exception."
            )

        if key in self.__bindings:
            return self.__bindings[key](self)
        return self.__items.get(key)

    def parse(self, text: str, **kwargs) -> str:
        """
        Replace keys surrounded by {{ and }} in the text with their values defined in the container.
        It will throw an exception if keys are not defined.
        """
        keys = extract_curly_braces(text)

        if len(keys) == 0:
            return text

        for key in keys:
            if kwargs.get(key):
                text = text.replace("{{" + key + "}}", str(kwargs.get(key)))
                continue

            if not self.has(key) and kwargs.get("throw"):
                raise BindingException.with_key(key)

            value = self.make(key)

            if value is not None:
                text = text.replace("{{" + key + "}}", str(value))

        if kwargs.get("recursive") is True:
            return self.parse(text)

        return text
