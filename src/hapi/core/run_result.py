class RunResult:
    def __init__(self, origin):
        self.origin = origin

        self.__outlog = origin.stdout.strip()
        self.__errlog = origin.stderr.strip()

    def trim(self):
        self.__outlog
