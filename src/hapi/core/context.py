import random
from typing import Any, Optional

from fabric import Result
from invoke import StreamWatcher

from ..exceptions import (
    ConfigurationError,
    ContextError,
    GracefulShutdown,
)
from ..utils import env_stringify, extract_curly_brackets
from .container import Container
from .io import InputOutput, Printer
from .remote import Remote
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

        self.__cwd: list[str] = []

    def io(self) -> InputOutput:
        """
        Return the IO instance of this context.

        :return InputOutput:
        """
        return self.printer.io

    def info(self, message: str):
        """
        Print an info message for this context.

        :param str message:
        """
        self.printer.print_info(self.remote, self.parse(message))

    def raise_error(self, message: str):
        """
        Raise a context error with the given message.

        :param str message:
        """
        raise ContextError(self.parse(message))

    def exec_task(self, task: Task):
        """
        Execute a task instance against the remote of this context.

        :param Task task:
        """
        self._before_exec_task(task)

        try:
            task.func(self._do_clone())
        except Exception as e:
            self._do_catch(task, e)

        self._after_exec_task(task)

    def put(self, key: str, value):
        self.container.put(key, value)

    def check(self, key: str) -> bool:
        return True if self.remote.has(key) else self.container.has(key)

    def cook(self, key: str, fallback: Any = None, throw: bool = False):
        """
        Return the value of a key from the remote or container.

        :param str key: The configuration key
        :param any fallback: The fallback value to return if the key aws not found
        :param bool throw: Determine if it should throw an exception if the key was not found
        :return any: The value of the key
        """

        if self.remote.has(key):
            return self.remote.make(key, fallback)

        if self.container.has(key):
            context = self._do_clone()
            return self.container.make(key, fallback, inject=context)

        if throw:
            raise ConfigurationError(f"Missing configuration: {key}")

        return fallback

    def parse(self, text: str) -> str:
        """
        Parse the given text and replace any curly brackets with the corresponding value.

        :param str text: Any text to parse
        :return str: The parsed text
        """
        keys = extract_curly_brackets(text)

        if len(keys) == 0:
            return text

        for key in keys:
            value = self.cook(key, throw=True)
            text = text.replace("{{" + key + "}}", str(value))

        return self.parse(text)

    def sudo(self, command: str, **kwargs):
        kwargs["sudo"] = True
        return self.run(command, **kwargs)

    def run(self, command: str, **kwargs):
        command = self._do_parse_command(command, env=kwargs.get("env"))

        sudo = kwargs.get("sudo") is True

        self._before_run_command(command, sudo)
        res = self._do_run(command, **kwargs)
        self._after_run_command(command)

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

    def _do_run(self, command: str, **kwargs):
        def process_line(line: str):
            self.printer.print_line(self.remote, line)

        class PrintWatcher(StreamWatcher):
            def __init__(self):
                super().__init__()
                self.last_pos = 0

            def submit(self, stream: str):
                last_end_line_pos = stream.rfind("\n")

                new_content = stream[self.last_pos : last_end_line_pos]

                if new_content:
                    self.last_pos = last_end_line_pos

                    lines = new_content.splitlines()

                    if lines:
                        for line in lines:
                            process_line(line)
                return []

        watcher = PrintWatcher()

        conn = self.remote.connect()

        if kwargs.get("sudo"):
            origin = conn.sudo(command, hide=True, watchers=[watcher])
        else:
            origin = conn.run(command, hide=True, watchers=[watcher])

        conn.close()

        res = RunResult(origin)

        return res

    def _do_catch(self, task: Task, ex: Exception):
        if isinstance(ex, GracefulShutdown):
            raise ex

        self._do_exec_list(task.failed)

        raise ex

    def _do_clone(self):
        return Context(self.container, self.remote, self.tasks, self.printer)

    def _do_exec_list(self, names: list[str]):
        if len(names) == 0:
            return
        for name in names:
            task = self.tasks.find(name)
            self.exec_task(task)

    def _do_parse_command(self, command: str, env: Optional[dict[str, str]] = None):
        cwd = " && cd ".join(self.__cwd)

        if cwd.strip() != "":
            command = f"cd {cwd} && ({command.strip()})"
        else:
            command = command.strip()

        if env:
            env_vars = env_stringify(env)
            command = f"export {env_vars}; {command}"

        return self.parse(command)

    def _before_exec_task(self, task: Task):
        if len(task.children) == 0:
            self.printer.print_exec_task(self.remote, task)

        self._do_exec_list(task.before)

    def _after_exec_task(self, task: Task):
        self.__cwd = []

        self._do_exec_list(task.after)

    def _before_run_command(self, command: str, sudo: bool = False):
        self.printer.print_run_command(self.remote, command, sudo)

    def _after_run_command(self, command: str):
        pass


class RunResult:
    def __init__(self, origin: Optional[Result] = None):
        self.origin: Optional[Result] = origin
        self.fetched: bool = False

    def fetch(self) -> str:
        if self.fetched:
            return ""

        self.fetched = True

        return self.origin.stdout.strip() if self.origin else ""
