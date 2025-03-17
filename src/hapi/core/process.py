import random

from fabric import Result
from invoke import StreamWatcher

from ..exceptions import ParsingRecurredKey
from ..log import Logger
from ..support import env_stringify, extract_curly_braces
from .container import Container
from .io import InputOutput
from .remote import Remote
from .task import Task, TaskBag


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

    def __init__(
        self, container: Container, tasks: TaskBag, io: InputOutput, log: Logger
    ):
        self.container = container
        self.tasks = tasks
        self.printer = Printer(io, log)

        self.__parsing_stack = {}

    def parse(self, text: str, remote: Remote = None) -> str:
        keys = extract_curly_braces(text)

        if len(keys) == 0:
            return text

        for key in keys:
            if remote and remote.has(key):
                text = text.replace("{{" + key + "}}", remote.make(key))
                if key in self.__parsing_stack:
                    del self.__parsing_stack[key]
            elif self.container.has(key):
                text = text.replace("{{" + key + "}}", str(self.container.make(key)))
                if key in self.__parsing_stack:
                    del self.__parsing_stack[key]
            elif key in self.__parsing_stack:
                raise ParsingRecurredKey.with_key(key)
            else:
                self.__parsing_stack[key] = True

        return self.parse(text, remote)

    def info(self, remote: Remote, message: str):
        message = self.parse(message, remote)
        self.printer.print_info(remote, message)

    def run_task(self, remote: Remote, task: Task):
        self._before_run_task(remote, task)
        task.func(self.container)
        self._after_run_task(remote, task)

    def run_tasks(self, remote: Remote, names: list[str]):
        if len(names) == 0:
            return
        for name in names:
            task = self.tasks.find(name)
            self.run_task(remote, task)

    def parse_command(self, remote: Remote, command: str, **kwargs):
        cwd = remote.make("cwd")

        if cwd is not None:
            command = f"cd {cwd} && ({command.strip()})"
        else:
            command = command.strip()

        command = self.parse(command, remote)

        return command

    def run_command(self, remote: Remote, command: str, **kwargs):
        command = self.parse_command(remote, command, **kwargs)

        self._before_run_command(remote, command, **kwargs)

        self.printer.print_command(remote, command)

        res = self._do_run_command(remote, command, **kwargs)

        self._after_run_command(remote, command, **kwargs)

        return res

    def run_test(self, remote: Remote, command: str, **kwargs):
        picked = "+" + random.choice(Runner.TEST_CHOICES)
        command = f"if {command}; then echo {picked}; fi"
        res = self.run_command(remote, command, **kwargs)
        return res.fetch() == picked

    def run_cat(self, remote: Remote, file: str, **kwargs):
        return self.run_command(remote, f"cat {file}", **kwargs).fetch()

    def _do_run_command(self, remote: Remote, command: str, **kwargs):
        def callback(_: str, buffer: str):
            self.printer.print_buffer(remote, buffer)

        class LogBuffer(StreamWatcher):
            def __init__(self):
                super().__init__()
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
                            callback("log", line)
                return (
                    []
                )  # Return an empty list as we don't need to submit any responses

        watcher = LogBuffer()

        if kwargs.get("env"):
            env_vars = env_stringify(kwargs.get("env"))
            command = f"export {env_vars}; {command}"

        conn = remote.connect()

        origin = conn.run(command, hide=True, watchers=[watcher])

        res = CommandResult(origin)

        return res

    def _before_run_task(self, remote: Remote, task: Task):
        self.printer.print_task(remote, task)

        self.container.put("current_remote", remote)
        self.container.put("current_task", task)

        self.run_tasks(remote, task.before)

    def _after_run_task(self, remote: Remote, task: Task):
        remote.put("cwd", None)
        self.run_tasks(remote, task.after)

    def _before_run_command(self, remote: Remote, command: str, **kwargs):
        pass

    def _after_run_command(self, remote: Remote, command: str, **kwargs):
        pass
