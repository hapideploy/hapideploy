import random
import typing

import typer
from typing_extensions import Annotated

from ..exceptions import StoppedException
from ..log import Logger, NoneStyle
from ..log.file_style import FileStyle
from .container import Container
from .io import ConsoleInputOutput, InputOutput
from .process import CommandRunner, Printer, RunOptions, TaskRunner
from .remote import Remote
from .task import Task


class Deployer(Container):
    def __init__(self, io: InputOutput = None, log: Logger = None):
        super().__init__()
        self.io = io if io else ConsoleInputOutput()
        self.log = log if log else NoneStyle()

        self.__remotes = []
        self.__tasks = {}
        self.__typer = typer.Typer()
        self.__running = {}
        self.__selected = []
        self.__bootstrapped = False
        self.__started = False

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
        self.__remotes.append(remote)
        return self

    def add_command(self, name: str, desc: str, func: typing.Callable):
        @self.__typer.command(name=name, help=desc)
        def general_command():
            func(self)

        return self

    def add_task(self, name: str, desc: str, func: typing.Callable):
        task = Task(name, desc, func)

        self.__tasks[name] = task

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
            self._bootstrap(
                selector=selector,
                stage=stage,
                quiet=quiet,
                normal=normal,
                detail=detail,
                debug=debug,
            )

            for remote in self.__selected:
                self._run_task(remote, task)

        return self

    def add_group(self, name: str, desc: str, names: list[str]):
        def func(dep: Deployer):
            for task_name in names:
                remote = dep.current_route()
                task = dep.__tasks.get(task_name)
                self._run_task(remote, task)

        desc = desc if desc else f'Group "{name}": ' + ", ".join(names)

        self.add_task(name, desc, func)

        return self

    def run(self, command: str, **kwargs):
        remote = self.current_route()

        cwd = self.__running.get("cwd")

        if cwd is not None:
            command = self.parse(f"cd {cwd} && ({command.strip()})")
        else:
            command = self.parse(command.strip())

        printer = Printer(self.io, self.log)
        runner = CommandRunner(printer, remote, command)
        options = RunOptions(env=kwargs.get("env"))

        self._before_command(runner)
        res = runner.run(options)
        self._after_command(runner)

        return res

    def cat(self, file: str) -> str:
        return self.run(f"cat {file}").fetch()

    def test(self, command: str) -> bool:
        picked = "+" + random.choice(
            [
                "accurate",
                "appropriate",
                "correct",
                "legitimate",
                "precise",
                "right",
                "true",
                "yes",
                "indeed",
            ]
        )
        res = self.run(f"if {command}; then echo {picked}; fi")
        return res.fetch() == picked

    def cd(self, cwd: str):
        self.__running["cwd"] = self.parse(cwd)
        return self

    def info(self, message: str):
        remote = self.current_route()

        self.io.writeln(
            f"[<primary>{remote.label}</primary>] <success>info</success> {self.parse(message)}"
        )

    def stop(self, message: str):
        raise StoppedException(self.parse(message))

    def current_route(self) -> Remote | None:
        if self.__running["remote"]:
            return self.__running["remote"]

        self.stop("No running remote is set.")

    def _bootstrap(self, **kwargs):
        if self.__bootstrapped:
            return

        if not self.__remotes:
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

        self.io = ConsoleInputOutput(
            kwargs.get("selector"), kwargs.get("stage"), verbosity
        )

        if self.has("log_file"):
            self.log = FileStyle(self.make("log_file"))

        self.__selected = [
            remote
            for remote in self.__remotes
            if self.io.selector == InputOutput.SELECTOR_DEFAULT
            or remote.label == self.io.selector
        ]

        self.put("stage", self.io.stage)

        self.__bootstrapped = True

    def _run_task(self, remote: Remote, task: Task):
        printer = Printer(self.io, self.log)
        runner = TaskRunner(printer, remote, task, self)

        self._before_task(runner)
        runner.run()
        self._after_task(runner)

    def _before_task(self, runner: TaskRunner):
        self.__running["remote"] = runner.remote
        self.__running["task"] = runner.task
        self.put("deploy_dir", self.parse(runner.remote.deploy_dir))
        pass

    def _after_task(self, _: TaskRunner):
        self.__running["cwd"] = None

    def _before_command(self, runner: CommandRunner):
        pass

    def _after_command(self, _: CommandRunner):
        pass
