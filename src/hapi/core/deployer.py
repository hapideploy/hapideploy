import random
import re
import typing

import typer
from typing_extensions import Annotated

from .config import Configuration
from .io import InputOutput
from .run_result import RunResult
from .task import TaskDefinition


class Deployer:
    __instance = None

    def __init__(self):
        self.config = Configuration()
        self.remotes = []
        self.tasks = []

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

    def load_io(self, io: InputOutput):
        self.io = io

        self.config.put("branch", io.branch)
        self.config.put("stage", io.stage)

    def add_task(self, name: str, desc: str, func: typing.Callable):
        task = TaskDefinition(name, desc, func)

        self.tasks.append(task)

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
                self.io.writeln(f"[{self.running_remote.label}] task {task.name}")
                func(self)

        return self

    def parse(self, text: str, params: dict = None):
        remote = self.running_remote

        if remote is not None:
            text = text.replace("{{deploy_dir}}", remote.deploy_dir)

        keys = self._extract_curly_braces(text)

        for key in keys:
            if params is not None and key in params:
                text = text.replace("{{" + key + "}}", str(params[key]))
                continue

            if self.config.has(key) is not True:
                raise RuntimeException(f"Configuration key {key} is not defined.")

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

    def run(self, command: str, **kwargs):
        parsed_command = self.parse(command)
        self.io.writeln(f"[{self.running_remote.label}] run {parsed_command}")
        origin = self.running_remote.connect().run(parsed_command, **kwargs)
        res = RunResult(origin)
        return res

    def log(self, message: str, channel: str = "out"):
        parsed = self.parse(message)
        self.io.writeln(f"[{self.running_remote.label}] {channel} {parsed}")
