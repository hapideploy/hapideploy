import random
import typing

import typer
from fabric import Connection
from typing_extensions import Annotated

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
        self.remotes = []
        self.tasks = {}
        self.running = {}
        self.io = None

    def parse(self, text: str, params: dict = None):
        remote = self.running.get("remote")

        if isinstance(remote, Remote):
            text = text.replace("{{deploy_dir}}", remote.deploy_dir)

        return super().parse(text, params)

    def add_task(self, name: str, desc: str, func: typing.Callable):
        task = Task(name, desc, func)

        self.tasks[name] = task

        @self.typer.command(name=name, help=desc)
        def task_command(
            selector: str = typer.Argument(default=InputOutput.SELECTOR_DEFAULT),
            branch: Annotated[
                str, typer.Option(help="The git repository branch.")
            ] = InputOutput.BRANCH_DEFAULT,
            stage: Annotated[
                str, typer.Option(help="The deploy stage.")
            ] = InputOutput.STAGE_DEFAULT,
            verbose: Annotated[bool, typer.Option(help="Print verbose output.")] = None,
            debug: Annotated[bool, typer.Option(help="Print debug output.")] = None,
            quiet: Annotated[
                bool, typer.Option(help="Do not print any output.")
            ] = None,
        ):
            if self.io is None:
                verbosity = InputOutput.VERBOSITY_NORMAL
                if quiet:
                    verbosity = InputOutput.VERBOSITY_QUIET
                elif debug:
                    verbosity = InputOutput.VERBOSITY_DEBUG
                elif verbose:
                    verbosity = InputOutput.VERBOSITY_VERBOSE

                self._load_io(InputOutput(selector, branch, stage, verbosity))

            remotes = [
                remote
                for remote in self.remotes
                if selector == InputOutput.SELECTOR_DEFAULT or remote.label == selector
            ]

            for remote in remotes:
                self.running["remote"] = remote
                self.run_task(task)

        return self

    def run_tasks(self, tasks: [str]):
        for task in tasks:
            self.run_task(task)

    def run_task(self, task):
        # TODO: If there is no running remote, exit?
        task = task if isinstance(task, Task) else self.tasks.get(task)
        self._begin_task(task)
        task.func(self)
        self._end_task(task)

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

    def cd(self, path: str):
        self.running["cd"] = path
        return self

    def run(self, runnable: str):
        remote = self._detect_running_remote()

        cd_dir = self.running.get("cd")

        if cd_dir is not None:
            command = self.parse(f"cd {cd_dir} && ({runnable.strip()})")
        else:
            command = self.parse(runnable.strip())

        if self.io.verbosity > InputOutput.VERBOSITY_NORMAL:
            self.log(channel="run", message=command)

        conn = Connection(host=remote.host, user=remote.user, port=remote.port)
        # TODO: Check the run result, raise an informative exception when needed.
        origin = conn.run(command, hide=True)
        res = RunResult(origin)

        if res.fetch() == "":
            return res

        if self.io.verbosity >= InputOutput.VERBOSITY_DEBUG:
            for line in res.lines():
                self.log(line)

        return res

    def log(self, message: str, channel: str = None):
        remote = self._detect_running_remote()

        parsed = self.parse(message)

        if channel:
            self.io.writeln(f"[{remote.label}] {channel} {parsed}")
        else:
            self.io.writeln(f"[{remote.label}] {parsed}")

    def info(self, message: str):
        if self.io.verbosity > InputOutput.VERBOSITY_NORMAL:
            self.log(message, "info")

    def stop(self, message: str):
        raise StoppedException(self.parse(message))

    def _load_io(self, io: InputOutput):
        self.io = io
        self.put("branch", io.branch)
        self.put("stage", io.stage)

    def _detect_running_remote(self) -> Remote:
        remote = self.running.get("remote")

        if isinstance(remote, Remote):
            return remote

        raise RuntimeException("The running remote is not set.")

    def _begin_task(self, task):
        self.log(task.name, channel="task")

    def _end_task(self, task):
        self.running["cd"] = None
