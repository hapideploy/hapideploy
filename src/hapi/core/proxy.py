from typing import Annotated, Optional

from typer import Argument, Option, Typer

from ..log import FileStyle, Logger, NoneStyle
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
from .io import ConsoleIO, InputOutput, Printer
from .remote import Remote, RemoteBag
from .task import Task, TaskBag


class Proxy:
    STAGE_DEV = "dev"

    def __init__(self, container: Container):
        self.console = Typer()

        self.container = container
        self.io = ConsoleIO()
        self.log: Logger = NoneStyle()

        self.remotes = RemoteBag()
        self.tasks = TaskBag()

        self.selected: list[Remote] = []

        self.current_remote: Optional[Remote] = None
        self.current_task: Optional[Task] = None

        self.prepared: bool = False
        self.started: bool = False

        self.__context: Optional[Context] = None

    def make_context(self, isolate=False) -> Context:
        if not self.current_remote:
            raise RuntimeError("There is no current remote.")

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

    def define_commands(self):
        commands = {
            "about": AboutCommand,
            "init": InitCommand,
            "tree": TreeCommand,
            "config:list": ConfigListCommand,
            "config:show": ConfigShowCommand,
            "remote:list": RemoteListCommand,
        }

        command_names = commands.keys()

        single_names: list[str] = []
        complex_names: list[str] = []

        for c_name in commands.keys():
            if ":" in c_name:
                complex_names.append(c_name)
            else:
                single_names.append(c_name)

        for task in self.tasks.all():
            if ":" in task.name:
                complex_names.append(task.name)
            else:
                single_names.append(task.name)

        single_names.sort()
        complex_names.sort()

        for name in single_names + complex_names:
            if name in command_names:
                cls = commands[name]
                cls(self.container, self.io, self.remotes, self.tasks).define_for(
                    self.console
                )
            else:
                task = self.tasks.find(name)
                self._do_define_task_command(task)

    def define_general_commands(self):
        for cls in [
            AboutCommand,
            ConfigListCommand,
            ConfigShowCommand,
            InitCommand,
            RemoteListCommand,
            TreeCommand,
        ]:
            cls(self.container, self.io, self.remotes, self.tasks).define_for(
                self.console
            )

    def define_task_commands(self):
        for task in self.tasks.all():
            self._do_define_task_command(task)

    def _do_define_task_command(self, task: Task):
        @self.console.command(name=task.name, help=task.desc)
        def task_handler(
            selector: str = Argument(
                default=RemoteBag.SELECTOR_ALL, help="The remote selector"
            ),
            stage: Annotated[
                str, Option(help="The deployment stage. E.g., dev, testing, production")
            ] = self.STAGE_DEV,
            put: Annotated[
                str,
                Option(
                    help="Set or override config items. E.g., --put=node_version=22.15.0,python_version=3.13"
                ),
            ] = "",
            config: Annotated[
                str,
                Option(
                    help="[Deprecated] Customize config items. E.g., --config=python_version=3.13"
                ),
            ] = "",
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
                    put=put,
                    config=config,  # TODO: [Deprecated] Use --put instead
                    quiet=quiet,
                    normal=normal,
                    detail=detail,
                    debug=debug,
                )

            self.current_task = task

            for remote in self.selected:
                self.current_remote = remote
                self.make_context().exec_task(task)
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

        selector = str(kwargs.get("selector"))

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
        config_str = kwargs.get("put") or kwargs.get("config")
        if config_str:
            # self.io.set_option('config', config_str)
            pairs = config_str.split(",")
            for pair in pairs:
                key, value = pair.split("=")
                self.container.put(key, value)

        if self.container.has("log_file"):
            self.log = FileStyle(str(self.container.make("log_file")))
