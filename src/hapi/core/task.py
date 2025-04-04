import typing

from ..exceptions import ItemNotFound, TaskNotFound
from ..support import Collection


class Task:
    HOOK_BEFORE = "before"
    HOOK_AFTER = "after"
    HOOK_FAILED = "failed"

    def __init__(self, name: str, desc: str, func: typing.Callable):
        self.name = name
        self.desc = desc
        self.func = func

        self.children = []
        self.before = []
        self.after = []
        self.failed = []


class TaskBag(Collection):
    def __init__(self):
        super().__init__(Task)

        self.filter_key(lambda name, task: task.name == name)

    def add(self, task: Task):
        return super().add(task)

    def find(self, name: str) -> Task:
        try:
            return super().find(name)
        except ItemNotFound:
            raise TaskNotFound.with_name(name)

    def all(self) -> list[Task]:
        return super().all()
