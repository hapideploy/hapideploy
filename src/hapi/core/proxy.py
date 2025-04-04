import random
from typing import Annotated

from fabric import Result
from invoke import StreamWatcher
from typer import Argument, Option, Typer

from ..__version import __version__
from ..exceptions import GracefulShutdown, KeyNotFound, StoppedException
from ..log import FileStyle, NoneStyle
from ..support import env_stringify, extract_curly_brackets
from .commands import ConfigListCommand, ConfigShowCommand, InitCommand, TreeCommand
from .container import Container
from .context import Context
from .io import ConsoleInputOutput, InputOutput, Printer
from .remote import Remote, RemoteBag
from .task import Task, TaskBag


class Proxy:
    def __init__(self, container: Container):
        self.container = container
        self.typer = Typer()

        self.io = ConsoleInputOutput()
        self.log = NoneStyle()

        self.remotes = RemoteBag()
        self.tasks = TaskBag()

        self.selected = []

        self.current_remote = None
        self.current_task = None

        self.prepared = False
        self.started = False

        self.__context = None

    def make_context(self, isolate=False) -> Context:
        if isolate is True:
            return Context(
                self.container,
                self.current_remote,
                self.tasks,
                Printer(self.io, self.log),
            )

        if self.__context is None:
            self.__context = Context(
                self.container,
                self.current_remote,
                self.tasks,
                Printer(self.io, self.log),
            )

        return self.__context

    def clear_context(self):
        self.__context = None

    def add_builtin_commands(self):
        @self.typer.command(name="about", help="Display the Hapi CLI information")
        def about():
            print(f"Hapi {__version__}")

        @self.typer.command(
            name="config:list", help="Display all pre-defined configuration items"
        )
        def config_list():
            ConfigListCommand(self.container)()

        @self.typer.command(
            name="config:show", help="Display a configuration item details"
        )
        def config_list(key: str = Argument(help="A configuration key")):
            ConfigShowCommand(self.container)(key)

        @self.typer.command(name="init", help="Initialize hapi files")
        def init():
            exit_code = InitCommand(self.io).execute()
            exit(exit_code)

        @self.typer.command(name="tree", help="Display the task-tree for a given task")
        def tree(task: str = Argument(help="Task to display the tree for")):
            TreeCommand(self.tasks, self.io)(task)

    def add_command_for(self, task: Task):
        @self.typer.command(name=task.name, help="[task] " + task.desc)
        def task_handler(
            selector: str = Argument(default=InputOutput.SELECTOR_ALL),
            stage: Annotated[
                str, Option(help="The deployment stage")
            ] = InputOutput.STAGE_DEV,
            options: Annotated[str, Option(help="Task options")] = None,
            quiet: Annotated[
                bool, Option(help="Do not print any output messages (level: 0)")
            ] = False,
            normal: Annotated[
                bool,
                Option(help="Print normal output messages (level: 1)"),
            ] = False,
            detail: Annotated[
                bool, Option(help="Print verbose output message (level: 2")
            ] = False,
            debug: Annotated[
                bool, Option(help="Print debug output messages (level: 3)")
            ] = False,
        ):
            if not self.prepared:
                self.prepare(
                    selector=selector,
                    stage=stage,
                    options=options,
                    quiet=quiet,
                    normal=normal,
                    detail=detail,
                    debug=debug,
                )

            self.current_task = task

            for remote in self.selected:
                self.current_remote = remote
                self.make_context().exec(task)
                self.clear_context()

            self.current_task = task

    def prepare(self, **kwargs):
        if self.prepared:
            return

        self.prepared = True

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

        self.io.selector = selector
        self.io.stage = stage
        self.io.verbosity = verbosity

        self.selected = self.remotes.filter(
            lambda remote: self.io.selector == InputOutput.SELECTOR_ALL
            or remote.label == self.io.selector
        )

        self.container.put("stage", stage)

        opts_str = kwargs.get("options")
        if opts_str:
            opts_items = opts_str.split(",")
            options = dict()
            for opt_item in opts_items:
                opt_key, opt_val = opt_item.split("=")
                options[opt_key] = opt_val
                self.container.put(opt_key, opt_val)

        if self.container.has("log_file"):
            self.log = FileStyle(self.container.make("log_file"))
