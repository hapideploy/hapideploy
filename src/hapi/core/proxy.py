import random

from invoke import StreamWatcher
from typer import Typer

from ..exceptions import KeyNotFound, StoppedException
from ..log import NoneStyle
from ..support import env_stringify, extract_curly_braces
from .container import Container
from .io import ConsoleInputOutput, InputOutput, Printer
from .remote import Remote, RemoteBag
from .task import Task, TaskBag


class Context:
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
        self, container: Container, remote: Remote, tasks: TaskBag, printer: Printer
    ):
        self.container = container
        self.remote = remote
        self.tasks = tasks
        self.printer = printer

        self.__cwd = []
        self.__parsing_stack = {}

    def io(self) -> InputOutput:
        return self.printer.io

    def exec(self, task: Task):
        self._before_exec(task)
        task.func(self._clone())
        self._after_exec(task)

    def check(self, key: str) -> bool:
        return True if self.remote.has(key) else self.container.has(key)

    def cook(self, key: str, fallback=None):
        if self.remote.has(key):
            return self.remote.make(key, fallback, throw=True)

        if self.container.has(key):
            return self.container.make(key, fallback, throw=True, inject=self._clone())

        return fallback

    def put(self, key: str, value):
        self.container.put(key, value)

    def parse(self, text: str) -> str:
        keys = extract_curly_braces(text)

        if len(keys) == 0:
            return text

        for key in keys:
            if self.remote.has(key):
                text = text.replace("{{" + key + "}}", self.remote.make(key))
            elif self.container.has(key):
                text = text.replace(
                    "{{" + key + "}}",
                    str(self.container.make(key, inject=self._clone())),
                )
            else:
                raise KeyNotFound("Key not found: " + key)

        return self.parse(text)

    def run(self, command: str, **kwargs):
        command = self._parse_command(command)

        self._before_run(command, **kwargs)
        res = self._do_run(command, **kwargs)
        self._after_run(command, **kwargs)

        return res

    def test(self, command: str, **kwargs):
        picked = "+" + random.choice(Context.TEST_CHOICES)
        command = f"if {command}; then echo {picked}; fi"
        res = self.run(command, **kwargs)
        return res.fetch() == picked

    def cat(self, file: str, **kwargs):
        return self.run(f"cat {file}", **kwargs).fetch()

    def which(self, command: str, **kwargs):
        return self.run(f"which {command}", **kwargs).fetch()

    def cd(self, cwd: str):
        self.__cwd.append(cwd)
        return self.remote.put("cwd", self.parse(cwd))

    def info(self, message: str):
        message = self.parse(message)
        self.printer.print_info(self.remote, message)

    def stop(self, message: str):
        raise StoppedException(self.parse(message))

    def _do_run(self, command: str, **kwargs):
        def callback(_: str, buffer: str):
            self.printer.print_buffer(self.remote, buffer)

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

        conn = self.remote.connect()

        origin = conn.run(command, hide=True, watchers=[watcher])

        res = CommandResult(origin)

        return res

    def _clone(self):
        return Context(self.container, self.remote, self.tasks, self.printer)

    def _exec_tasks_by_name(self, names: list[str]):
        if len(names) == 0:
            return
        for name in names:
            task = self.tasks.find(name)
            self.exec(task)

    def _parse_command(self, command: str):
        cwd = " && cd ".join(self.__cwd)

        if cwd.strip() != "":
            command = f"cd {cwd} && ({command.strip()})"
        else:
            command = command.strip()

        command = self.parse(command)

        return command

    def _before_exec(self, task: Task):
        self.printer.print_task(self.remote, task)

        self._exec_tasks_by_name(task.before)

    def _after_exec(self, task: Task):
        self.__cwd = []

        self._exec_tasks_by_name(task.after)

    def _before_run(self, command: str, **kwargs):
        self.printer.print_command(self.remote, command)

    def _after_run(self, command: str, **kwargs):
        pass


class Proxy:
    def __init__(self, container: Container):
        self.container = container
        self.typer = Typer()

        self.io = ConsoleInputOutput()
        self.log = NoneStyle()

        self.remotes = RemoteBag()
        self.tasks = TaskBag()

        self.selected = []

        self.current_remote = None
        self.current_task = None

        self.prepared = False
        self.started = False

        self.__context = None

    def context(self, isolate=False) -> Context:
        if isolate is True:
            return Context(
                self.container,
                self.current_remote,
                self.tasks,
                Printer(self.io, self.log),
            )

        if self.__context is None:
            self.__context = Context(
                self.container,
                self.current_remote,
                self.tasks,
                Printer(self.io, self.log),
            )

        return self.__context

    def clear_context(self):
        self.__context = None


from fabric import Result


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
