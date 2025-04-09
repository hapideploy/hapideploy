from typing import Annotated

from typer import Argument, Option, Typer

from ..log import FileStyle, NoneStyle
from .commands import (
    AboutCommand,
    ConfigListCommand,
    ConfigShowCommand,
    InitCommand,
    RemoteListCommand,
    TreeCommand,
)
from .container import Container
from .context import Context
from .io import ConsoleInputOutput, InputOutput, Printer
from .remote import RemoteBag
from .task import Task, TaskBag


class Proxy:
    STAGE_DEV = "dev"

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

        @self.typer.command(name=RemoteListCommand.NAME, help=RemoteListCommand.DESC)
        def remote_list(
            selector: str = Argument(
                default=RemoteBag.SELECTOR_ALL, help="The remote selector"
            )
        ):
            self.io.set_argument("selector", selector)
            exit_code = RemoteListCommand(self.remotes, self.io).execute()
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
            selector: str = Argument(
                default=RemoteBag.SELECTOR_ALL, help="The remote selector"
            ),
            stage: Annotated[
                str, Option(help="The deployment stage. E.g., dev, testing, production")
            ] = self.STAGE_DEV,
            config: Annotated[
                str,
                Option(
                    help="Customize config items. E.g., --config=python_version=3.13"
                ),
            ] = None,
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
                    config=config,
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

        self._do_prepare_verbosity(**kwargs)

        self._do_prepare_selector(**kwargs)

        self._do_prepare_stage(**kwargs)

        self._do_prepare_config(**kwargs)

    def _do_prepare_verbosity(self, **kwargs):
        verbosity = InputOutput.NORMAL

        if kwargs.get("quiet"):
            verbosity = InputOutput.QUIET
        elif kwargs.get("normal"):
            verbosity = InputOutput.NORMAL
        elif kwargs.get("detail"):
            verbosity = InputOutput.DETAIL
        elif kwargs.get("debug"):
            verbosity = InputOutput.DEBUG

        self.io.verbosity = verbosity

    def _do_prepare_selector(self, **kwargs):
        if self.remotes.empty():
            raise RuntimeError(f"The are no remotes defined.")

        selector = kwargs.get("selector")

        self.io.set_argument("selector", selector)

        self.selected = self.remotes.select(selector)

        if len(self.selected) == 0:
            raise RuntimeError(f"No remotes match the selector: {selector}")

    def _do_prepare_stage(self, **kwargs):
        stage = kwargs.get("stage")

        if stage:
            self.io.set_argument("stage", stage)

        self.container.put("stage", stage)

    def _do_prepare_config(self, **kwargs):
        config_str = kwargs.get("config")
        if config_str:
            # self.io.set_option('config', config_str)
            pairs = config_str.split(",")
            for pair in pairs:
                key, value = pair.split("=")
                self.container.put(key, value)

        if self.container.has("log_file"):
            self.log = FileStyle(self.container.make("log_file"))
