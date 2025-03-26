import typing

import typer
from typing_extensions import Annotated

from ..__version import __version__
from ..exceptions import CurrentRemoteNotSet, CurrentTaskNotSet, InvalidHookKind
from ..log import FileStyle
from .commands import ConfigListCommand, ConfigShowCommand, TreeCommand
from .container import Container
from .io import InputOutput
from .proxy import Proxy
from .remote import Remote
from .task import Task


class Deployer(Container):
    def __init__(self):
        super().__init__()
        self.__proxy = Proxy(self)

    def prepared(self) -> bool:
        return self.__proxy.prepared

    def prepare(self, **kwargs):
        if self.prepared():
            return

        self.__proxy.prepared = True

        verbosity = InputOutput.NORMAL

        if kwargs.get("quiet"):
            verbosity = InputOutput.QUIET
        elif kwargs.get("normal"):
            verbosity = InputOutput.NORMAL
        elif kwargs.get("detail"):
            verbosity = InputOutput.DETAIL
        elif kwargs.get("debug"):
            verbosity = InputOutput.DEBUG

        selector = kwargs.get("selector")
        stage = kwargs.get("stage")

        self.__proxy.io.selector = selector
        self.__proxy.io.stage = stage
        self.__proxy.io.verbosity = verbosity

        if self.has("log_file"):
            self.__proxy.log = FileStyle(self.make("log_file"))

        self.__proxy.selected = self.remotes().filter(
            lambda remote: self.__proxy.io.selector == InputOutput.SELECTOR_ALL
            or remote.label == self.__proxy.io.selector
        )

        self.put("stage", stage)

        opts_str = kwargs.get("options")
        if opts_str:
            opts_items = opts_str.split(",")
            options = dict()
            for opt_item in opts_items:
                opt_key, opt_val = opt_item.split("=")
                options[opt_key] = opt_val
                self.put(opt_key, opt_val)

    def started(self) -> bool:
        return self.__proxy.started

    def start(self):
        if self.started():
            return

        self.__proxy.started = True

        self._add_builtin_commands()

        for task in self.tasks().all():
            self._add_command_for(task)

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

    def register_task(self, name: str, desc: str, func: typing.Callable):
        task = Task(name, desc, func)

        self.tasks().add(task)

        return task

    def register_group(self, name: str, desc: str, names: list[str]):
        def func(_):
            for task_name in names:
                task = self.tasks().find(task_name)
                self.__proxy.current_task = task
                self.__proxy.context().exec(task)
                self.__proxy.clear_context()

        self.register_task(name, desc, func).children = names

        return self

    def register_hook(self, kind: str, name: str, do):
        task = self.tasks().find(name)

        if kind == "before":
            task.before = do if isinstance(do, list) else [do]
        elif kind == "after":
            task.after = do if isinstance(do, list) else [do]
        else:
            raise InvalidHookKind(
                f"Invalid hook kind: {kind}. Chose either 'before' or 'after'."
            )

        task.hook = do

        return self

    def _add_builtin_commands(self):
        @self.__proxy.typer.command(name="about", help="Display the Hapi CLI version")
        def about():
            print(f"Hapi {__version__}")

        @self.__proxy.typer.command(
            name="config:list", help="Display all pre-defined configuration items"
        )
        def config_list():
            ConfigListCommand(self)()

        @self.__proxy.typer.command(
            name="config:show", help="Display a configuration item details"
        )
        def config_list(key: str):
            ConfigShowCommand(self)(key)

        @self.__proxy.typer.command(
            name="tree", help="Display the task-tree for a given task"
        )
        def tree(task: str = typer.Argument(help="Task to display the tree for")):
            TreeCommand(self)(task)

    def _add_command_for(self, task: Task):
        @self.__proxy.typer.command(name=task.name, help="[task] " + task.desc)
        def task_handler(
            selector: str = typer.Argument(default=InputOutput.SELECTOR_ALL),
            stage: Annotated[
                str, typer.Option(help="The deployment stage")
            ] = InputOutput.STAGE_DEV,
            options: Annotated[str, typer.Option(help="Task options")] = None,
            quiet: Annotated[
                bool, typer.Option(help="Do not print any output messages (level: 0)")
            ] = False,
            normal: Annotated[
                bool,
                typer.Option(help="Print normal output messages (level: 1)"),
            ] = False,
            detail: Annotated[
                bool, typer.Option(help="Print verbose output message (level: 2")
            ] = False,
            debug: Annotated[
                bool, typer.Option(help="Print debug output messages (level: 3)")
            ] = False,
        ):
            if not self.prepared():
                self.prepare(
                    selector=selector,
                    stage=stage,
                    options=options,
                    quiet=quiet,
                    normal=normal,
                    detail=detail,
                    debug=debug,
                )

            self.__proxy.current_task = task

            for remote in self.__proxy.selected:
                self.__proxy.current_remote = remote
                self.__proxy.context().exec(task)
                self.__proxy.clear_context()

            self.__proxy.current_task = task
