import random
import typing

import typer
import yaml
from typing_extensions import Annotated

from ..exceptions import RuntimeException, StoppedException
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
        self.__discovered = []

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
                selector=selector,
                stage=stage,
                quiet=quiet,
                normal=normal,
                detail=detail,
                debug=debug,
            )

            for remote in self.selected:
                self._run_task(remote, task)

        return self

    def add_group(self, name: str, desc: str, names: list[str]):
        def func(dep: Deployer):
            for task_name in names:
                remote = dep.current_route()
                task = dep.tasks.get(task_name)
                self._run_task(remote, task)

        desc = desc if desc else f'Group "{name}": ' + ", ".join(names)

        self.add_task(name, desc, func)

        return self

    def task(self, name: str, desc: str = None):
        desc = desc if desc is not None else name

        def caller(func: typing.Callable):
            self.add_task(name, desc, func)

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

    def host(self, **kwargs):
        kwargs["host"] = kwargs.get("name")
        del kwargs["name"]
        remote = Remote(**kwargs)
        self.remotes.append(remote)
        return self

    def discover(self, file: str = "inventory.yml"):
        if file in self.__discovered:
            return

        with open(file) as stream:
            self.__discovered.append(file)

            loaded_data = yaml.safe_load(stream)

            if (
                loaded_data is None
                or isinstance(loaded_data.get("hosts"), dict) is False
            ):
                raise RuntimeException(f'"hosts" definition is invalid.')

            for name, data in loaded_data["hosts"].items():
                if data.get("host"):
                    self.host(
                        name=data.get("host"),
                        user=data.get("user"),
                        port=data.get("port"),
                        deploy_dir=data.get("deploy_dir"),
                        pemfile=data.get("pemfile"),
                        label=name,
                    )
                else:
                    self.host(name=name, **data)

    def bootstrap(self, **kwargs):
        if self.__bootstrapped:
            return

        if not self.remotes:
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

        self.io = InputOutput(kwargs.get("selector"), kwargs.get("stage"), verbosity)
        self.logger = StreamStyle()

        self.selected = [
            remote
            for remote in self.remotes
            if self.io.selector == InputOutput.SELECTOR_DEFAULT
            or remote.label == self.io.selector
        ]

        self.put("stage", self.io.stage)

        self.__bootstrapped = True

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
