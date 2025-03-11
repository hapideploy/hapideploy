class InputOutput:
    VERBOSITY_QUIET = 1
    VERBOSITY_NORMAL = 2
    VERBOSITY_VERBOSE = 3
    VERBOSITY_DEBUG = 4

    SELECTOR_DEFAULT = "all"
    BRANCH_DEFAULT = "main"
    STAGE_DEFAULT = "dev"
    VERBOSITY_DEFAULT = 2  # VERBOSITY_NORMAL

    def __init__(self, selector: str, branch: str, stage: str, verbosity: int = None):
        self.selector = selector
        self.branch = branch
        self.stage = stage
        self.verbosity = (
            InputOutput.VERBOSITY_DEFAULT if verbosity is None else verbosity
        )

    def writeln(self, line: str = ""):
        if self.verbosity == InputOutput.VERBOSITY_QUIET:
            return

        print(line.replace("<success>", "").replace("</success>", ""))
