from typing import Annotated

from typer import Argument, Option, Typer

from ..log import FileStyle, NoneStyle
from .commands import (
    AboutCommand,
    ConfigListCommand,
    ConfigShowCommand,
    InitCommand,
    TreeCommand,
)
from .container import Container
from .context import Context
from .io import ConsoleInputOutput, InputOutput, Printer
from .remote import RemoteBag
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

    def define_general_commands(self):
        @self.typer.command(name=AboutCommand.NAME, help=AboutCommand.DESC)
        def about():
            exit_code = AboutCommand(self.io).execute()
            exit(exit_code)

        @self.typer.command(name=ConfigListCommand.NAME, help=ConfigListCommand.DESC)
        def config_list():
            exit_code = ConfigListCommand(self.container).execute()
            exit(exit_code)

        @self.typer.command(name=ConfigShowCommand.NAME, help=ConfigShowCommand.DESC)
        def config_show(key: str = Argument(help="A configuration key")):
            self.io.set_argument("key", key)
            exit_code = ConfigShowCommand(self.container, self.io).execute()
            exit(exit_code)

        @self.typer.command(name=InitCommand.NAME, help=InitCommand.DESC)
        def init():
            exit_code = InitCommand(self.io).execute()
            exit(exit_code)

        @self.typer.command(name=TreeCommand.NAME, help=TreeCommand.DESC)
        def tree(task: str = Argument(help="Task to display the tree for")):
            self.io.set_argument("task", task)
            exit_code = TreeCommand(self.tasks, self.io).execute()
            exit(exit_code)

    def define_task_commands(self):
        for task in self.tasks.all():
            self._do_define_task_command(task)

    def _do_define_task_command(self, task: Task):
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
