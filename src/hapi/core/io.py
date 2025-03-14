import re

import typer


class InputOutput:
    QUIET = 0
    NORMAL = 1
    DETAIL = 2
    DEBUG = 3

    SELECTOR_DEFAULT = "all"
    STAGE_DEFAULT = "dev"

    def __init__(self, selector: str = None, stage: str = None, verbosity: int = None):
        self.selector = selector if selector else InputOutput.SELECTOR_DEFAULT
        self.stage = stage if stage else InputOutput.STAGE_DEFAULT
        self.verbosity = verbosity if verbosity else InputOutput.NORMAL

        self.replacements = dict(
            primary=[r"\<primary\>([^}]*)\<\/primary\>", typer.colors.CYAN],
            success=[r"\<success\>([^}]*)\<\/success\>", typer.colors.GREEN],
            danger=[r"\<danger\>([^}]*)\<\/danger\>", typer.colors.RED],
        )

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
                surrounded = piece.strip(f"<{tag}>").strip(f"</{tag}>")
                text = text.replace(piece, typer.style(surrounded, fg=fg))

        return text


class ConsoleInputOutput(InputOutput):
    def _do_write(self, text: str, newline: bool = False):
        decorated = self.decorate(text)
        typer.echo(decorated, nl=newline)


class CacheInputOutput(InputOutput):
    def __init__(self, selector: str = None, stage: str = None, verbosity: int = None):
        super().__init__(selector, stage, verbosity)

        self.items = []

    def _do_write(self, text: str, newline: bool = False):
        decorated = self.decorate(text) + ("\n" if newline else "")
        self.items.append(decorated)
