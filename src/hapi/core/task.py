from typing import Any, Callable

from ..collect import Collection
from ..exceptions import ItemNotFound, TaskNotFound


class Task:
    HOOK_BEFORE = "before"
    HOOK_AFTER = "after"
    HOOK_FAILED = "failed"

    def __init__(self, name: str, desc: str, func: Callable[[Any], Any]):
        self.name = name
        self.desc = desc
        self.func = func

        self.children: list[str] = []
        self.before: list[str] = []
        self.after: list[str] = []
        self.failed: list[str] = []


class TaskBag(Collection):
    def __init__(self):
        super().__init__(Task)

        self.find_using(lambda name, task: task.name == name)

    def add(self, task: Task):
        return super().add(task)

    def find(self, name: str) -> Task:
        try:
            return super().find(name)
        except ItemNotFound:
            raise TaskNotFound.with_name(name)

    def match(self, callback: Callable[[Task], bool]) -> Task:
        try:
            return super().match(callback)
        except ItemNotFound:
            raise TaskNotFound("No tasks match the given callback.")

    def filter(self, callback: Callable[[Task], bool]) -> list[Task]:
        return super().filter(callback)

    def all(self) -> list[Task]:
        return super().all()
