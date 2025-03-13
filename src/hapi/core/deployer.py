import random
import typing

import typer
from typing_extensions import Annotated

from ..exceptions import StoppedException
from ..log import NoneStyle, StreamStyle
from .container import Container
from .io import InputOutput
from .process import CommandRunner, RunOptions, RunPrinter, TaskRunner
from .remote import Remote
from .task import Task


class Deployer(Container):
    def __init__(self):
        super().__init__()
        self.typer = typer.Typer()
        self.logger = NoneStyle()
        self.remotes = []
        self.tasks = {}
        self.io = None

        self.running = {}
        self.selected = []

        self.__current_runner = None
        self.__bootstrapped = False

    def bootstrap(self, options: dict):
        if self.__bootstrapped:
            return

        self.__bootstrapped = True

        verbosity = InputOutput.NORMAL

        if options.get("quiet"):
            verbosity = InputOutput.QUIET
        elif options.get("normal"):
            verbosity = InputOutput.NORMAL
        elif options.get("detail"):
            verbosity = InputOutput.DETAIL
        elif options.get("debug"):
            verbosity = InputOutput.DEBUG

        self.io = InputOutput(options.get("selector"), options.get("stage"), verbosity)
        self.logger = StreamStyle()

        self.selected = [
            remote
            for remote in self.remotes
            if self.io.selector == InputOutput.SELECTOR_DEFAULT
            or remote.label == self.io.selector
        ]

        self.put("stage", self.io.stage)

    def add_task(self, name: str, desc: str, func: typing.Callable):
        task = Task(name, desc, func)

        self.tasks[name] = task

        @self.typer.command(name=name, help=desc)
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
                {
                    "selector": selector,
                    "stage": stage,
                    "quiet": quiet,
                    "normal": normal,
                    "detail": detail,
                    "debug": debug,
                }
            )

            for remote in self.selected:
                self._run_task(remote, task)

        return self

    def add_group(self, name: str, do: list[str], desc: str = None):
        def func(dep: Deployer):
            for task_name in do:
                remote = dep.current_route()
                task = dep.tasks.get(task_name)
                self._run_task(remote, task)

        desc = desc if desc else f'Group "{name}": ' + ", ".join(do)

        self.add_task(name, desc, func)

        return self

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
        self.running["cd"] = cwd
        return self

    def run(self, command: str, **kwargs):
        remote = self.current_route()

        cwd = self.running.get("cd")

        if cwd is not None:
            command = self.parse(f"cd {cwd} && ({command.strip()})")
        else:
            command = self.parse(command.strip())

        printer = RunPrinter(self.io, self.logger)
        runner = CommandRunner(printer, remote, command)
        options = RunOptions(env=kwargs.get("env"))

        self._before_command(runner)
        res = runner.run(options)
        self._after_command(runner)

        return res

    def info(self, message: str):
        remote = self.current_route()

        self.logger.writeln(f"[{remote.label}] info {self.parse(message)}")

    def stop(self, message: str):
        raise StoppedException(self.parse(message))

    def current_route(self) -> Remote | None:
        if self.__current_runner:
            return self.__current_runner.remote

        self.stop("No running remote is set.")

    def _run_task(self, remote: Remote, task: Task):
        printer = RunPrinter(self.io, self.logger)
        runner = TaskRunner(printer, remote, task, self)

        self._before_task(runner)
        runner.run()
        self._after_task(runner)

    def _before_task(self, runner: TaskRunner):
        self.__current_runner = runner
        self.put("deploy_dir", self.parse(runner.remote.deploy_dir))
        pass

    def _after_task(self, _: TaskRunner):
        self.running["cd"] = None

    def _before_command(self, runner: CommandRunner):
        self.__current_runner = runner
        pass

    def _after_command(self, _: CommandRunner):
        pass
