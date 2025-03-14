import shlex
import typing

from fabric import Result
from invoke import StreamWatcher

from ..log import Logger
from .io import InputOutput
from .remote import Remote
from .task import Task


def env_stringify(env: dict) -> str:
    items = []
    for name, value in env.items():
        items.append(f"%s=%s" % (name, shlex.quote(str(value))))
    return " ".join(items)


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

    def print_task(self, remote: Remote, task: Task):
        self.log.info(f"[{remote.label}] task {task.name}")

        if self.io.verbosity >= InputOutput.NORMAL:
            text = f"[<primary>{remote.label}</primary>] <success>task</success> {task.name}"
            self.io.writeln(text)
            # self.logger.writeln(text)

    def print_command(self, remote: Remote, command: str):
        self.log.info(f"[{remote.label}] run {command}")

        if self.io.verbosity >= InputOutput.DETAIL:
            text = (
                f"[<primary>{remote.label}</primary>] <success>run</success> {command}"
            )
            self.io.writeln(text)

    def print_buffer(self, remote: Remote, buffer: str):
        self.log.debug(f"[{remote.label}] {buffer}")

        if self.io.verbosity >= InputOutput.DEBUG:
            text = f"[<primary>{remote.label}</primary>] {buffer}"
            self.io.writeln(text)


class RunOptions:
    def __init__(self, env: dict = None):
        self.env = env


class RunResult:
    def __init__(self, origin: Result):
        self.origin = origin

        self.__output = None

    def lines(self):
        return self.fetch().split("\n")

    def fetch(self):
        if self.__output is None:
            self.__output = self.origin.stdout.strip()
        return self.__output


class Runner:
    def __init__(self, printer: Printer, remote: Remote):
        self.printer = printer
        self.remote = remote


class CommandRunner(Runner):
    def __init__(self, printer: Printer, remote: Remote, command: str):
        super().__init__(printer, remote)
        self.command = command

    def run(self, options: RunOptions = None) -> RunResult:
        # E.g. [ubuntu] run if [ -f ~/deploy/.dep/latest_release ]; then echo +true; fi
        self.printer.print_command(self.remote, self.command)

        # E.g. [ubuntu] +true
        def callback(_: str, buffer: str):
            self.printer.print_buffer(self.remote, buffer)

        watcher = LogBuffer(callback)

        command = self.command

        if options and options.env:
            env_vars = env_stringify(options.env)
            command = f"export {env_vars}; {self.command}"

        conn = self.remote.connect()

        origin = conn.run(command, hide=True, watchers=[watcher])

        return RunResult(origin)


class TaskRunner(Runner):
    def __init__(self, printer: Printer, remote: Remote, task: Task, deployer):
        super().__init__(printer, remote)

        self.task = task
        self.deployer = deployer

    def run(self):
        # E.g: [ubuntu] task deploy:start
        self.printer.print_task(self.remote, self.task)
        self.task.func(self.deployer)
