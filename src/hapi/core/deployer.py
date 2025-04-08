import typing

from ..exceptions import InvalidHookKind, RemoteNotFound, TaskNotFound
from .container import Container
from .proxy import Context, Proxy
from .remote import Remote, RemoteBag
from .task import Task, TaskBag


class Deployer(Container):
    def __init__(self):
        super().__init__()
        self.__proxy = Proxy(self)

    def start(self):
        if self.__proxy.started:
            return

        self.__proxy.started = True

        self.__proxy.define_general_commands()

        self.__proxy.define_task_commands()

        self.__proxy.typer()

    def get_remotes(self) -> RemoteBag:
        return self.__proxy.remotes

    def get_tasks(self) -> TaskBag:
        return self.__proxy.tasks

    def define_remote(self, **kwargs) -> Remote:
        remote = Remote(**kwargs)
        try:
            self.__proxy.remotes.find(remote.key)
            raise ValueError(f'Remote "{remote.key}" already exists.')
        except RemoteNotFound:
            self.__proxy.remotes.add(remote)
        return remote

    def define_task(
        self, name: str, desc: str, func: typing.Callable[[Context], any]
    ) -> Task:
        try:
            task = self.__proxy.tasks.find(name)
            task.desc = desc
            task.func = func
        except TaskNotFound:
            task = Task(name, desc, func)
            self.__proxy.tasks.add(task)
        return task

    def define_group(self, name: str, desc: str, names: str | list[str]) -> Task:
        children = names if isinstance(names, list) else [names]

        for child in children:
            self.__proxy.tasks.find(child)

        def func(_):
            for t_name in children:
                task = self.__proxy.tasks.find(t_name)
                self.__proxy.current_task = task
                self.__proxy.make_context().exec(task)
                self.__proxy.clear_context()

        group = self.define_task(name, desc, func)

        group.children = children

        return group

    def define_hook(self, kind: str, name: str, do: str | list[str]):
        task = self.__proxy.tasks.find(name)

        t_names = do if isinstance(do, list) else [do]

        for t_name in t_names:
            self.__proxy.tasks.find(t_name)

        if kind == Task.HOOK_BEFORE:
            task.before = t_names
        elif kind == Task.HOOK_AFTER:
            task.after = t_names
        elif kind == Task.HOOK_FAILED:
            task.failed = t_names
        else:
            raise InvalidHookKind(
                f"Invalid hook kind: {kind}. Choose either '{Task.HOOK_BEFORE}', '{Task.HOOK_AFTER}' or '{Task.HOOK_FAILED}'."
            )

        return self
