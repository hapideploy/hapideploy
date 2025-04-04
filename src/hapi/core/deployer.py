import typing

from ..exceptions import CurrentRemoteNotSet, CurrentTaskNotSet, InvalidHookKind
from .container import Container
from .proxy import Context, Proxy
from .remote import Remote, RemoteBag
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

        for task in self.__proxy.tasks.all():
            self.__proxy.add_command_for(task)

        self.__proxy.typer()

    def get_remotes(self) -> RemoteBag:
        return self.__proxy.remotes

    def register_remote(self, **kwargs) -> Remote:
        remote = Remote(**kwargs)
        self.__proxy.remotes.add(remote)
        return remote

    def register_task(
        self, name: str, desc: str, func: typing.Callable[[Context], any]
    ) -> Task:
        task = Task(name, desc, func)

        self.__proxy.tasks.add(task)

        return task

    def register_group(self, name: str, desc: str, names: str | list[str]) -> Task:
        children = names if isinstance(names, list) else [names]

        def func(_):
            for task_name in children:
                task = self.__proxy.tasks.find(task_name)
                self.__proxy.current_task = task
                self.__proxy.make_context().exec(task)
                self.__proxy.clear_context()

        group_task = self.register_task(name, desc, func)

        group_task.children = children

        return group_task

    def register_hook(self, kind: str, name: str, do: str | list[str]):
        task = self.__proxy.tasks.find(name)

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
