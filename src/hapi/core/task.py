import typing


class Task:
    def __init__(self, name: str, desc: str, func: typing.Callable):
        self.name = name
        self.desc = desc
        self.func = func

        self.before = []
        self.after = []

class Collection:
    def __init__(self, key_name: str):
        self.key_name = key_name
        self.items = []

    def add(self, item):
        self.items.append(item)

    def all(self):
        return self.items

class TaskBag(Collection):
    def find(self, key: str):
        for task in self.items:
            if task.name == key:
                return task

        return None
