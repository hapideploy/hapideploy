import typing


class Task:
    def __init__(self, name: str, desc: str, func: typing.Callable):
        self.name = name
        self.desc = desc
        self.func = func
