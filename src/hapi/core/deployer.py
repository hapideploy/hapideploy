import random
import typing

import typer
from fabric import Connection
from typing_extensions import Annotated

from hapi.core.run_command import RunCommand
from hapi.core.run_task import RunTask
from hapi.log import NoneStyle, StreamStyle

from ..exceptions import RuntimeException, StoppedException
from .container import Container
from .io import InputOutput
from .remote import Remote
from .run_result import RunResult
from .task import Task


class Deployer(Container):
    def __init__(self):
        super().__init__()
        self.typer = typer.Typer()
        self.logger = NoneStyle()
        self.remotes = []
        self.tasks = {}
        self.running = {}
        self.io = None

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

    # @overridde
    def parse(self, text: str, params: dict = None):
        remote = self.running.get("remote")

        if isinstance(remote, Remote):
            text = text.replace("{{deploy_dir}}", remote.deploy_dir)

        if isinstance(self.io, InputOutput):
            text = text.replace("{{stage}}", self.io.stage)

        return super().parse(text, params)

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

            remotes = [
                remote
                for remote in self.remotes
                if selector == InputOutput.SELECTOR_DEFAULT or remote.label == selector
            ]

            for remote in remotes:
                self.running["remote"] = remote
                self.run_task(task)

        return self

    def run_task(self, task):
        name = task if isinstance(task, str) else task.name
        task = task if isinstance(task, Task) else self.tasks.get(name)

        if task is None:
            self.stop(f'Task "{name}" is not defined.')

        remote = self._detect_running_remote()

        run_task = RunTask(remote, task)

        self._before_task(run_task)
        task.func(self)
        self._after_task(run_task)

    def run_tasks(self, tasks: [str]):
        for task in tasks:
            self.run_task(task)

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

    def cd(self, cd_dir: str):
        self.running["cd"] = cd_dir
        return self

    def run(self, command: str):
        remote = self._detect_running_remote()

        cd_dir = self.running.get("cd")

        if cd_dir is not None:
            command = self.parse(f"cd {cd_dir} && ({command.strip()})")
        else:
            command = self.parse(command.strip())

        run_command = RunCommand(remote, command)
        self._before_run(run_command)
        run_command.run()
        self._after_run(run_command)

        return run_command.res

    def info(self, message: str):
        remote = self._detect_running_remote()

        self.logger.writeln(f"[{remote.label}] info {self.parse(message)}")

    def stop(self, message: str):
        raise StoppedException(self.parse(message))

    def _detect_running_remote(self) -> Remote:
        remote = self.running.get("remote")

        if isinstance(remote, Remote):
            return remote

        self.stop("No running remote is set.")

    def _before_task(self, run_task: RunTask):
        if self.io.verbosity >= InputOutput.NORMAL:
            self.logger.writeln(
                f"[%s] task %s" % (run_task.remote.label, run_task.task.name)
            )

    def _after_task(self, task):
        self.running["cd"] = None

    def _before_run(self, run_command: RunCommand):
        if self.io.verbosity >= InputOutput.DETAIL:
            self.logger.writeln(
                f"[%s] run %s" % (run_command.remote.label, run_command.command)
            )

    def _after_run(self, run_command: RunCommand):
        if self.io.verbosity >= InputOutput.DEBUG:
            if run_command.res.fetch() == "":
                return

            for line in run_command.res.lines():
                self.logger.writeln(f"[%s] %s " % (run_command.remote.label, line))
