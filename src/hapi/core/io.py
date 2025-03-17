import re

import typer


class InputOutput:
    QUIET = 0
    NORMAL = 1
    DETAIL = 2
    DEBUG = 3

    SELECTOR_ALL = "all"
    STAGE_DEV = "dev"

    def __init__(self, selector: str = None, stage: str = None, verbosity: int = None):
        self.selector = selector if selector is not None else InputOutput.SELECTOR_ALL
        self.stage = stage if stage is not None else InputOutput.STAGE_DEV
        self.verbosity = verbosity if verbosity is not None else InputOutput.NORMAL

        self.replacements = dict(
            primary=[r"\<primary\>([^}]*)\<\/primary\>", typer.colors.CYAN],
            success=[r"\<success\>([^}]*)\<\/success\>", typer.colors.GREEN],
            info=[r"\<info\>([^}]*)\<\/info\>", typer.colors.BLUE],
            comment=[r"\<comment\>([^}]*)\<\/comment\>", typer.colors.YELLOW],
            warning=[r"\<warning\>([^}]*)\<\/warning\>", typer.colors.YELLOW],
            danger=[r"\<danger\>([^}]*)\<\/danger\>", typer.colors.RED],
        )

    def debug(self) -> bool:
        return self.verbosity == InputOutput.DEBUG

    def write(self, text: str = ""):
        self._do_write(text, False)

    def writeln(self, text: str = ""):
        self._do_write(text, True)

    def _do_write(self, text: str, newline: bool = False):
        raise NotImplemented

    def decorate(self, text: str):
        for tag, data in self.replacements.items():
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


class ConsoleInputOutput(InputOutput):
    def _do_write(self, text: str, newline: bool = False):
        decorated = self.decorate(text)
        typer.echo(decorated, nl=newline)


class ArrayInputOutput(InputOutput):
    def __init__(self, selector: str = None, stage: str = None, verbosity: int = None):
        super().__init__(selector, stage, verbosity)

        self.items = []

    def _do_write(self, text: str, newline: bool = False):
        decorated = self.decorate(text) + ("\n" if newline else "")
        self.items.append(decorated)
