import random

from fabric import Result
from invoke import StreamWatcher

from ..exceptions import (
    ConfigurationError,
    GracefulShutdown,
    StoppedException,
)
from ..support import env_stringify, extract_curly_brackets
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

        self.__cwd = []

    def io(self) -> InputOutput:
        return self.printer.io

    def exec(self, task: Task):
        self._before_exec(task)

        try:
            task.func(self._do_clone())
        except Exception as e:
            self._do_catch(task, e)

        self._after_exec(task)

    def put(self, key: str, value):
        self.container.put(key, value)

    def check(self, key: str) -> bool:
        return True if self.remote.has(key) else self.container.has(key)

    def cook(self, key: str, fallback: any = None, throw: bool = False):
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

    def run(self, command: str, **kwargs):
        command = self._do_parse_command(command, **kwargs)

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
        self.printer.print_info(self.remote, self.parse(message))

    def stop(self, message: str):
        raise StoppedException(self.parse(message))

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

        origin = conn.run(command, hide=True, watchers=[watcher])

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
            self.exec(task)

    def _do_parse_command(self, command: str, **kwargs):
        cwd = " && cd ".join(self.__cwd)

        if cwd.strip() != "":
            command = f"cd {cwd} && ({command.strip()})"
        else:
            command = command.strip()

        if kwargs.get("env"):
            env_vars = env_stringify(kwargs.get("env"))
            command = f"export {env_vars}; {command}"

        return self.parse(command)

    def _before_exec(self, task: Task):
        self.printer.print_task(self.remote, task)

        self._do_exec_list(task.before)

    def _after_exec(self, task: Task):
        self.__cwd = []

        self._do_exec_list(task.after)

    def _before_run(self, command: str, **kwargs):
        self.printer.print_command(self.remote, command)

    def _after_run(self, command: str, **kwargs):
        pass


class RunResult:
    def __init__(self, origin: Result = None):
        self.origin = origin
        self.fetched = False

    def fetch(self) -> str:
        if self.fetched:
            return ""

        self.fetched = True

        return self.origin.stdout.strip()
