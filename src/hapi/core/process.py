from fabric import Result

from ..log import Logger
from .io import InputOutput
from .remote import Remote
from .task import Task


class Printer:
    def __init__(self, io: InputOutput, log: Logger):
        self.io = io
        self.log = log

    def _do_print(self, remote: Remote, message: str):
        self.io.writeln(f"[<primary>{remote.label}</primary>] {message}")

    def print_info(self, remote: Remote, message: str):
        self.log.debug(f"[{remote.label}] INFO {message}")

        if self.io.verbosity > InputOutput.QUIET:
            self._do_print(remote, f"<info>INFO</info> {message}")

    def print_task(self, remote: Remote, task: Task):
        self.log.debug(f"[{remote.label}] TASK {task.name}")

        if self.io.verbosity >= InputOutput.NORMAL:
            self._do_print(remote, f"<success>TASK</success> {task.name}")

    def print_command(self, remote: Remote, command: str):
        self.log.info(f"[{remote.label}] RUN {command}")

        if self.io.verbosity >= InputOutput.DETAIL:
            self._do_print(remote, f"<comment>RUN</comment> {command}")

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
