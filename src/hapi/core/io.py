import re

import typer

from ..log import Logger
from .remote import Remote
from .task import Task


class InputOutput:
    QUIET = 0
    NORMAL = 1
    DETAIL = 2
    DEBUG = 3

    SELECTOR_ALL = "all"
    STAGE_DEV = "dev"

    def __init__(self, selector: str = None, stage: str = None, verbosity: int = None):
        self.arguments = dict()

        self.selector = selector if selector is not None else InputOutput.SELECTOR_ALL
        self.stage = stage if stage is not None else InputOutput.STAGE_DEV
        self.verbosity = verbosity if verbosity is not None else InputOutput.NORMAL

    def set_argument(self, name: str, value: str):
        self.arguments[name] = value

    def get_argument(self, name: str, fallback=None):
        return self.arguments[name] if name in self.arguments else fallback

    def quiet(self) -> bool:
        return self.verbosity == InputOutput.QUIET

    def normal(self) -> bool:
        return self.verbosity == InputOutput.NORMAL

    def detail(self) -> bool:
        return self.verbosity == InputOutput.DETAIL

    def debug(self) -> bool:
        return self.verbosity == InputOutput.DEBUG

    def write(self, text: str = ""):
        self._do_write(text, False)

    def writeln(self, text: str = ""):
        self._do_write(text, True)

    def error(self, text: str = ""):
        prefix = typer.style(" ERROR ", bg=typer.colors.RED)
        self._do_write("", True)
        self._do_write(f"  {prefix} {text}", True)
        self._do_write("", True)

    def success(self, text: str = ""):
        prefix = typer.style(" SUCCESS ", bg=typer.colors.GREEN)
        self._do_write("", True)
        self._do_write(f"  {prefix} {text}", True)
        self._do_write("", True)

    @staticmethod
    def decorate(text: str):
        replacements = dict(
            primary=[r"\<primary\>([^}]*)\<\/primary\>", typer.colors.CYAN],
            success=[r"\<success\>([^}]*)\<\/success\>", typer.colors.GREEN],
            info=[r"\<info\>([^}]*)\<\/info\>", typer.colors.BLUE],
            comment=[r"\<comment\>([^}]*)\<\/comment\>", typer.colors.YELLOW],
            warning=[r"\<warning\>([^}]*)\<\/warning\>", typer.colors.YELLOW],
            danger=[r"\<danger\>([^}]*)\<\/danger\>", typer.colors.RED],
        )
        for tag, data in replacements.items():
            pattern = data[0]
            fg = data[1]

            regexp = re.compile(pattern)

            times = 0

            while regexp.search(text):
                times += 1
                if times == 100:
                    raise RuntimeError(f"Too many {tag} wrappers.")
                l = text.find(f"<{tag}>")
                r = text.find(f"</{tag}>")
                piece = text[l : r + len(f"</{tag}>")]
                surrounded = piece.replace(f"<{tag}>", "").replace(f"</{tag}>", "")
                text = text.replace(piece, typer.style(surrounded, fg=fg))

        return text

    def _do_write(self, text: str, newline: bool = False):
        raise NotImplemented


class ConsoleInputOutput(InputOutput):
    def _do_write(self, text: str, newline: bool = False):
        decorated = InputOutput.decorate(text)
        typer.echo(decorated, nl=newline)


class ArrayInputOutput(InputOutput):
    def __init__(self, selector: str = None, stage: str = None, verbosity: int = None):
        super().__init__(selector, stage, verbosity)

        self.items = []

    def _do_write(self, text: str, newline: bool = False):
        decorated = InputOutput.decorate(text) + ("\n" if newline else "")
        self.items.append(decorated)


class Printer:
    def __init__(self, io: InputOutput, log: Logger):
        self.io = io
        self.log = log

    def print_task(self, remote: Remote, task: Task):
        self.log.debug(f"[{remote.label}] TASK {task.name}")

        if self.io.verbosity >= InputOutput.NORMAL:
            self._do_print(remote, f"<success>TASK</success> {task.name}")

    def print_command(self, remote: Remote, command: str):
        self.log.debug(f"[{remote.label}] RUN {command}")

        if self.io.verbosity >= InputOutput.DETAIL:
            self._do_print(remote, f"<comment>RUN</comment> {command}")

    def print_line(self, remote: Remote, line: str):
        self.log.debug(f"[{remote.label}] {line}")

        if self.io.verbosity >= InputOutput.DEBUG:
            self._do_print(remote, line)

    def print_info(self, remote: Remote, message: str):
        self.log.debug(f"[{remote.label}] INFO {message}")

        if self.io.verbosity >= InputOutput.NORMAL:
            self._do_print(remote, f"<info>INFO</info> {message}")

    def _do_print(self, remote: Remote, message: str):
        self.io.writeln(f"[<primary>{remote.label}</primary>] {message}")
