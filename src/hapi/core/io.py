class InputOutput:
    QUIET = 0
    NORMAL = 1
    DETAIL = 2
    DEBUG = 3

    SELECTOR_DEFAULT = "all"
    STAGE_DEFAULT = "dev"

    def __init__(self, selector: str, stage: str, verbosity: int):
        self.selector = selector
        self.stage = stage
        self.verbosity = verbosity

    def write(self, text: str = ""):
        self._do_write(text, False)

    def writeln(self, text: str = ""):
        self._do_write(text, True)

    def _do_write(self, text: str, newline: bool = False):
        parsed = self._decorate(text)
        print(parsed, end="\n" if newline else "")

    def _decorate(self, text: str = ""):
        return text.replace("<success>", "").replace("</success>", "")
