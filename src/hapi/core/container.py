from typing import Any, Callable


class BindingValue:
    def __init__(self, value: Any):
        self.value = value


class BindingCallback:
    def __init__(self, callback: Callable[[Any], Any]):
        self.callback = callback


class Container:
    __instance = None

    def __init__(self):
        self.__bindings = {}

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
        self.__bindings[key] = BindingValue(value)
        return self

    def add(self, key: str, value):
        """
        Append one or more values to the given key in the container.

        :param str key: The unified key (identifier) in the container.
        :param value: It can be a single value such as int, str or a list.
        """
        if self.__bindings.get(key) is None:
            self.__bindings[key] = BindingValue([])

        if isinstance(self.__bindings[key].value, list) is False:
            raise ValueError(f'The value associated with "{key}" is not a list.')

        if isinstance(value, list):
            for v in value:
                self.__bindings[key].value.append(v)
        else:
            self.__bindings[key].value.append(value)

        return self

    def bind(self, key: str, callback: Callable[[Any], Any]):
        """
        Bind a callback to its key in the container.
        """
        self.__bindings[key] = BindingCallback(callback)
        return self

    def resolve(self, key: str):
        """
        Bind a callback to its key in the container using decorator.

            @container.resolve
            def resolve_tools(_)
                return ['poetry', 'typer', 'fabric']

        :param str key: The unified key (identifier) in the container.
        """

        def wrapper(func: Callable[[Any], Any]):
            self.bind(key, func)

        return wrapper

    def has(self, key: str) -> bool:
        """
        Determine if the given key exists in the container.

        :param str key: The key (identifier) needs to be checked.
        """
        return key in self.__bindings

    def make(self, key: str, fallback: Any = None, throw=None, inject=None):
        """
        Resolve an item from the container.

        :param str key: The key (identifier) needs to be resolved.
        :param any fallback: This will be returned if key does not exist.
        :param bool|Exception throw: Determine if it should raise an exception if key does not exist.
        :param any inject: The value to be injected into the callback.
        """
        if not self.has(key):
            if throw is None or throw is False:
                return fallback

            if throw is True:
                raise ValueError(f'The key "{key}" is not defined in the container.')

            if isinstance(throw, Exception):
                raise throw

            raise ValueError(
                "throw must be either None, bool or an instance of Exception."
            )

        binding = self.__bindings[key]

        return (
            binding.value
            if isinstance(binding, BindingValue)
            else binding.callback(inject if inject else self)
        )

    def all(self) -> dict:
        return self.__bindings
