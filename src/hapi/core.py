"""habideploy package."""

__version__ = "0.1.0"

import random
import re
import typing

import typer
import yaml
from fabric import Connection
from typing_extensions import Annotated


class LogicException(Exception):
    pass


class RuntimeException(Exception):
    pass


class Configuration:
    def __init__(self):
        self.__items = {}

    def put(self, key: str, value):
        self.__items[key] = value
        return self

    def add(self, key: str, value):
        if self.__items.get(key) is None:
            self.__items[key] = []

        if isinstance(self.__items[key], list) is False:
            raise LogicException(f'The value associated with "{key}" is not a list.')

        if isinstance(value, list):
            for v in value:
                self.__items[key].append(v)
        else:
            self.__items[key].append(value)

        return self

    def has(self, key: str):
        return key in self.__items

    def find(self, key: str):
        return self.__items.get(key)

    def all(self) -> dict:
        return self.__items


class RemoteDefinition:
    def __init__(
        self,
        host: str,
        user: str = "hapi",
        port: int = 22,
        deploy_dir: str = "~/deploy/{{stage}}",
        label: str = None,
    ):
        self.host = host
        self.user = user
        self.port = port
        self.deploy_dir = deploy_dir
        self.label = host if label is None else label
        self.id = f"{self.user}@{self.host}:{self.port}"

    def connect(self):
        return Connection(host=self.host, user=self.user)


class TaskDefinition:
    def __init__(self, name: str, desc: str, func: typing.Callable):
        self.name = name
        self.desc = desc
        self.func = func


class InputOutput:
    VERBOSITY_QUIET = 1
    VERBOSITY_NORMAL = 2
    VERBOSITY_VERBOSE = 3
    VERBOSITY_DEBUG = 4

    SELECTOR_DEFAULT = "all"
    BRANCH_DEFAULT = "main"
    STAGE_DEFAULT = "dev"
    VERBOSITY_DEFAULT = 2  # VERBOSITY_NORMAL

    def __init__(self, selector: str, branch: str, stage: str, verbosity: int = None):
        self.selector = selector
        self.branch = branch
        self.stage = stage
        self.verbosity = (
            InputOutput.VERBOSITY_DEFAULT if verbosity is None else verbosity
        )

    def writeln(self, line: str = ""):
        if self.verbosity == InputOutput.VERBOSITY_QUIET:
            return

        print(line.replace("<success>", "").replace("</success>", ""))


class RunResult:
    def __init__(self, origin):
        self.origin = origin

        self.__outlog = origin.stdout.strip()
        self.__errlog = origin.stderr.strip()

    def trim(self):
        self.__outlog


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
        picked = "+" + random.choice([
            "accurate",
            "appropriate",
            "correct",
            "legitimate",
            "precise",
            "right",
            "true",
            "yes",
            "indeed",
        ])
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


class Program:
    def __init__(self):
        self.deployer = Deployer()

        # TODO: Register default commands.
        @self.deployer.typer.command(name="about", help=f"Display program information")
        def about():
            print(f"HapiDeploy {__version__}")

        @self.deployer.typer.command(name="list", help=f"List commands")
        def list():
            print("List commands")

    def start(self):
        # TODO: If there are no remotes, try to load from inventory.yml file
        self.deployer.typer()

    def put(self, key: str, value):
        self.deployer.config.put(key, value)
        return self

    def add(self, key: str, value):
        self.deployer.config.add(key, value)
        return self

    def host(self, **kwargs):
        kwargs["host"] = kwargs.get("name")
        del kwargs["name"]
        remote = RemoteDefinition(**kwargs)
        self.deployer.remotes.append(remote)
        return self

    def load(self, file: str = "inventory.yml"):
        with open(file) as stream:
            try:
                loaded_data = yaml.safe_load(stream)

                if isinstance(loaded_data.get("hosts"), dict) is False:
                    raise RuntimeException(f'"hosts" definition is invalid.')

                for name, data in loaded_data["hosts"].items():
                    self.host(name=name, **data)
            except yaml.YAMLError as exc:
                # TODO: throw RuntimeException
                print(exc)

    def task(self, name: str, desc: str = None):
        desc = desc if desc is not None else name

        def caller(call: typing.Callable):
            self.deployer.add_task(name, desc, call)

            def wrapper(*args, **kwargs):
                # Do something before the function call
                print("Before the function call")

                # Call the original function
                result = func(*args, **kwargs)

                # Do something after the function call
                print("After the function call")
                return result

            return wrapper

        return caller
