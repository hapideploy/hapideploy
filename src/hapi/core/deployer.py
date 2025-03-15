import random
import typing

import typer
from typing_extensions import Annotated

from ..exceptions import StoppedException
from ..log import Logger, NoneStyle
from ..log.file_style import FileStyle
from .container import Container
from .io import ConsoleInputOutput, InputOutput
from .process import Printer, Runner
from .remote import Remote, RemoteBag
from .task import Task, TaskBag


class Deployer(Container):
    def __init__(self, io: InputOutput = None, log: Logger = None):
        super().__init__()
        self.__io = io if io else ConsoleInputOutput()
        self.__log = log if log else NoneStyle()
        self.__runner = Runner(self)

        # TODO: self.__commands = CommandBag()
        self.__tasks = TaskBag()
        self.__remotes = RemoteBag()

        self.__typer = typer.Typer()
        self.__selected = []
        self.__bootstrapped = False
        self.__started = False

    def io(self):
        return self.__io

    def log(self):
        return self.__log

    def tasks(self):
        return self.__tasks

    def remotes(self):
        return self.__remotes

    def started(self):
        return self.__started

    def start(self):
        if self.__started:
            return

        self.__started = True

        self.__typer()

    def add_remote(self, **kwargs):
        remote = Remote(**kwargs)
        self.remotes().add(remote)
        return remote

    def add_command(self, name: str, desc: str, func: typing.Callable):
        @self.__typer.command(name=name, help=desc)
        def general_command():
            func(self)

        return self

    def add_task(self, name: str, desc: str, func: typing.Callable):
        task = Task(name, desc, func)

        self.__tasks.add(task)

        @self.__typer.command(name=name, help=desc)
        def task_command(
            selector: str = typer.Argument(default=InputOutput.SELECTOR_DEFAULT),
            stage: Annotated[
                str, typer.Option(help="The deployment stage")
            ] = InputOutput.STAGE_DEFAULT,
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
            self.bootstrap(
                selector=selector,
                stage=stage,
                quiet=quiet,
                normal=normal,
                detail=detail,
                debug=debug,
            )

            for remote in self.__selected:
                self.__runner.run_task(remote, task)

        return self

    def add_group(self, name: str, desc: str, names: list[str]):
        def func(dep: Deployer):
            for task_name in names:
                remote = dep.current_route()
                task = dep.tasks().find(task_name)
                self.__runner.run_task(remote, task)

        desc = desc if desc else f'Group "{name}": ' + ", ".join(names)

        self.add_task(name, desc, func)

        return self

    def run_task(self, name: str):
        remote = self.current_route()
        task = self.tasks().find(name)

        self.__runner.run_task(remote, task)

    def run(self, command: str, **kwargs):
        return self.__runner.run_command(self.current_route(), command, **kwargs)

    def test(self, command: str) -> bool:
        return self.__runner.run_test(self.current_route(), command)

    def cat(self, file: str) -> str:
        return self.__runner.run_cat(self.current_route(), file)

    def cd(self, location: str):
        self.current_route().put("location", self.parse(location))
        return self

    def info(self, message: str):
        printer = Printer(self.__io, self.__log)
        printer.print_info(self.current_route(), self.parse(message))

    def stop(self, message: str):
        raise StoppedException(self.parse(message))

    def current_route(self) -> Remote:
        if not self.has("current_remote"):
            self.stop("No running remote is set.")

        return self.make("current_remote")

    def before(self, name: str, do):
        task = self.__tasks.find(name)
        task.before = do if isinstance(do, list) else [do]
        return self

    def after(self, name: str, do):
        task = self.__tasks.find(name)
        task.after = do if isinstance(do, list) else [do]
        return self

    def bootstrap(self, **kwargs):
        if self.__bootstrapped:
            return

        self.__bootstrapped = True

        if self.remotes().empty():
            self.stop("There are no remotes. Please register at least 1.")

        verbosity = InputOutput.NORMAL

        if kwargs.get("quiet"):
            verbosity = InputOutput.QUIET
        elif kwargs.get("normal"):
            verbosity = InputOutput.NORMAL
        elif kwargs.get("detail"):
            verbosity = InputOutput.DETAIL
        elif kwargs.get("debug"):
            verbosity = InputOutput.DEBUG

        self.__io = ConsoleInputOutput(
            kwargs.get("selector"), kwargs.get("stage"), verbosity
        )

        if self.has("log_file"):
            self.__log = FileStyle(self.make("log_file"))

        self.__selected = self.remotes().filter(
            lambda remote: self.__io.selector == InputOutput.SELECTOR_DEFAULT
            or remote.label == self.__io.selector
        )

        self.put("stage", self.__io.stage)

        if isinstance(kwargs.get("runner"), Runner):
            self.__runner = kwargs.get("runner")

        return self
