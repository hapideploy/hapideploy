import random
import typing

from fabric import Result
from invoke import StreamWatcher

from ..log import Logger
from ..support import env_stringify
from .io import InputOutput
from .remote import Remote
from .task import Task


class LogBuffer(StreamWatcher):
    def __init__(self, callback: typing.Callable):
        super().__init__()
        self.callback = callback
        self.last_pos = 0

    def submit(self, stream: str):
        # Find new lines since last position
        new_content = stream[self.last_pos :]
        if new_content:
            # Update last position
            self.last_pos = len(stream)
            # Process any new complete lines
            lines = new_content.splitlines()
            if lines:
                for line in lines:
                    self.callback("log", line)
        return []  # Return an empty list as we don't need to submit any responses


class Printer:
    def __init__(self, io: InputOutput, log: Logger):
        self.io = io
        self.log = log

    def print(self, remote: Remote, message: str):
        self.io.writeln(f"[<primary>{remote.label}</primary>] {message}")

    def print_info(self, remote: Remote, message: str):
        self.log.debug(f"[{remote.label}] INFO {message}")

        if self.io.verbosity > InputOutput.QUIET:
            self.print(remote, f"<info>INFO</info> {message}")

    def print_task(self, remote: Remote, task: Task):
        self.log.debug(f"[{remote.label}] TASK {task.name}")

        if self.io.verbosity >= InputOutput.NORMAL:
            self.print(remote, f"<success>TASK</success> {task.name}")

    def print_command(self, remote: Remote, command: str):
        self.log.info(f"[{remote.label}] RUN {command}")

        if self.io.verbosity >= InputOutput.DETAIL:
            self.print(remote, f"<comment>RUN</comment> {command}")

    def print_buffer(self, remote: Remote, buffer: str):
        self.log.debug(f"[{remote.label}] {buffer}")

        if self.io.verbosity >= InputOutput.DEBUG:
            self.io.writeln(f"[<primary>{remote.label}</primary>] {buffer}")


class CommandResult:
    def __init__(self, origin: Result = None):
        self.origin = origin

        self.fetched = False

        self.__output = None

    def fetch(self) -> str:
        if self.fetched:
            return ""

        self.fetched = True

        return self.origin.stdout.strip()


class Runner:
    TEST_CHOICES = [
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

    def __init__(self, deployer):
        self.deployer = deployer

    def printer(self):
        return Printer(self.deployer.io(), self.deployer.log())

    def run_task(self, remote: Remote, task: Task):
        self._before_task(remote, task)
        self.printer().print_task(remote, task)
        task.func(self.deployer)
        self._after_task(remote, task)

    def _before_task(self, remote: Remote, task: Task):
        self.deployer.put("current_remote", remote)
        self.deployer.put("current_task", task)
        self.deployer.put(
            "deploy_path", self.deployer.parse(remote.make("deploy_path"))
        )
        self.run_tasks(remote, task.before)

    def _after_task(self, remote: Remote, task: Task):
        remote.put("cwd", None)
        self.run_tasks(remote, task.after)

    def run_tasks(self, remote: Remote, names: list[str]):
        if len(names) == 0:
            return
        for name in names:
            task = self.deployer.tasks().find(name)
            self.run_task(remote, task)

    def _do_run_command(self, remote: Remote, command: str, **kwargs):
        def callback(_: str, buffer: str):
            self.printer().print_buffer(remote, buffer)

        watcher = LogBuffer(callback)

        if kwargs.get("env"):
            env_vars = env_stringify(kwargs.get("env"))
            command = f"export {env_vars}; {command}"

        conn = remote.connect()

        origin = conn.run(command, hide=True, watchers=[watcher])

        res = CommandResult(origin)

        return res

    def parse_command(self, remote: Remote, command: str, **kwargs):
        cwd = remote.make("cwd")

        if cwd is not None:
            command = f"cd {cwd} && ({command.strip()})"
            command = self.deployer.parse(command)

        command = remote.parse(command, throw=False, recursive=False)
        command = self.deployer.parse(command)
        return command

    def run_command(self, remote: Remote, command: str, **kwargs):
        command = self.parse_command(remote, command, **kwargs)

        self._before_command(remote, command, **kwargs)

        self.printer().print_command(remote, command)

        res = self._do_run_command(remote, command, **kwargs)

        self._after_command(remote, command, **kwargs)

        return res

    def run_test(self, remote: Remote, command: str, **kwargs):
        picked = "+" + random.choice(Runner.TEST_CHOICES)
        command = f"if {command}; then echo {picked}; fi"
        res = self.run_command(remote, command, **kwargs)
        return res.fetch() == picked

    def run_cat(self, remote: Remote, file: str, **kwargs):
        return self.run_command(remote, f"cat {file}", **kwargs).fetch()

    def _before_command(self, remote: Remote, command: str, **kwargs):
        pass

    def _after_command(self, remote: Remote, command: str, **kwargs):
        pass
