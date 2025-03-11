import random
import re
import typing

import typer
from fabric import Connection
from typing_extensions import Annotated

from ..exceptions import RuntimeException
from .config import Config
from .io import InputOutput
from .run_result import RunResult
from .task import Task


class Deployer:
    __instance = None

    def __init__(self):
        self.config = Config()
        self.remotes = []
        self.tasks = {}

        self.typer = typer.Typer()
        self.io = None
        self.running_remote = None

    @staticmethod
    def set_instance(instance):
        Deployer.__instance = instance

    @staticmethod
    def get_instance():
        if Deployer.__instance is None:
            Deployer.__instance = Deployer()
        return Deployer.__instance

    @staticmethod
    def _extract_curly_braces(text):
        pattern = r"\{\{([^}]*)\}\}"
        matches = re.findall(pattern, text)
        return matches

    # Proxy methods
    def put(self, key: str, value):
        self.config.put(key, value)
        return self

    def stop(self, message: str):
        raise RuntimeException(self.parse(message))

    def load_io(self, io: InputOutput):
        self.io = io

        self.config.put("branch", io.branch)
        self.config.put("stage", io.stage)

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
            quiet: Annotated[
                bool, typer.Option(help="Do not print any output.")
            ] = None,
            verbose: Annotated[bool, typer.Option(help="Print debug output.")] = None,
        ):
            if self.io is None:
                verbosity = InputOutput.VERBOSITY_NORMAL
                if quiet:
                    verbosity = InputOutput.VERBOSITY_QUIET
                elif verbose:
                    verbosity = InputOutput.VERBOSITY_DEBUG

                self.load_io(InputOutput(selector, branch, stage, verbosity))

            remotes = [
                remote
                for remote in self.remotes
                if selector == InputOutput.SELECTOR_DEFAULT or remote.label == selector
            ]

            for remote in remotes:
                self.running_remote = remote
                self.run_task(task)

        return self

    def begin_task(self, task):
        self.log(task.name, channel="task")

    def end_task(self, task):
        # self.log(f'end {task.name}', channel='task')
        pass

    def run_task(self, task):
        # TODO: If there is no running remote, exit?
        task = task if isinstance(task, Task) else self.tasks.get(task)
        self.begin_task(task)
        task.func(self)
        self.end_task(task)

    def parse(self, text: str, params: dict = None):
        # TODO: If there is no running remote, exit?
        remote = self.running_remote

        if remote is not None:
            text = text.replace("{{deploy_dir}}", remote.deploy_dir)

        keys = self._extract_curly_braces(text)

        for key in keys:
            if params is not None and key in params:
                text = text.replace("{{" + key + "}}", str(params[key]))
                continue

            if self.config.has(key) is not True:
                raise RuntimeException(f"Config key {key} is not defined.")

            value = self.config.find(key)

            if value is not None:
                text = text.replace("{{" + key + "}}", str(value))

        keys = self._extract_curly_braces(text)

        if len(keys) > 0:
            return self.parse(text, params)

        return text

    def cat(self, file: str) -> str:
        self.run(f"cat {file}")
        return "1"

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
        return res.trim() == picked

    def run(self, runnable: str, **kwargs):
        remote = self._detect_running_remote()

        command = self.parse(runnable.strip())
        self.log(channel="run", message=command)

        conn = Connection(host=remote.host, user=remote.user, port=remote.port)
        # TODO: Check the run result, raise an informative exception when needed.
        origin = conn.run(command, hide=True)
        res = RunResult(origin)

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

    def _detect_running_remote(self):
        # TODO: Throw an exception if no running remote is present.
        return self.running_remote
