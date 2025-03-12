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
