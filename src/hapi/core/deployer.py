import typing

from ..exceptions import CurrentRemoteNotSet, CurrentTaskNotSet, InvalidHookKind
from .container import Container
from .proxy import Context, Proxy
from .remote import Remote
from .task import Task


class Deployer(Container):
    def __init__(self):
        super().__init__()
        self.__proxy = Proxy(self)

    def started(self) -> bool:
        return self.__proxy.started

    def start(self):
        if self.started():
            return

        self.__proxy.started = True

        self.__proxy.add_builtin_commands()

        for task in self.tasks().all():
            self.__proxy.add_command_for(task)

        self.__proxy.typer()

    def io(self):
        return self.__proxy.io

    def log(self):
        return self.__proxy.log

    def remotes(self):
        return self.__proxy.remotes

    def tasks(self):
        return self.__proxy.tasks

    def current_remote(self, **kwargs) -> Remote:
        throw = True if "throw" not in kwargs else kwargs.get("throw")

        if not self.__proxy.current_remote and throw is True:
            raise CurrentRemoteNotSet("The current remote is not set.")

        return self.__proxy.current_remote

    def current_task(self, **kwargs) -> Task:
        throw = True if "throw" not in kwargs else kwargs.get("throw")

        if not self.__proxy.current_task and throw:
            raise CurrentTaskNotSet("The current task is not set.")

        return self.__proxy.current_task

    def register_command(self, name: str, desc: str, func: typing.Callable):
        @self.__proxy.typer.command(name=name, help=desc)
        def command_handler():
            func(self)

    def register_remote(self, **kwargs):
        remote = Remote(**kwargs)
        self.remotes().add(remote)
        return remote

    def register_task(
        self, name: str, desc: str, func: typing.Callable[[Context], any]
    ):
        task = Task(name, desc, func)

        self.tasks().add(task)

        return task

    def register_group(self, name: str, desc: str, names: str | list[str]):
        children = names if isinstance(names, list) else [names]

        def func(_):
            for task_name in children:
                task = self.tasks().find(task_name)
                self.__proxy.current_task = task
                self.__proxy.context().exec(task)
                self.__proxy.clear_context()

        group_task = self.register_task(name, desc, func)

        group_task.children = children

        return group_task

    def register_hook(self, kind: str, name: str, do: str | list[str]):
        task = self.tasks().find(name)

        if kind == "before":
            task.before = do if isinstance(do, list) else [do]
        elif kind == "after":
            task.after = do if isinstance(do, list) else [do]
        elif kind == "failed":
            task.failed = do if isinstance(do, list) else [do]
        else:
            raise InvalidHookKind(
                f"Invalid hook kind: {kind}. Chose either 'before', 'after' or 'failed'."
            )

        task.hook = do

        return self
