from fabric import Result


class RunResult:
    def __init__(self, origin: Result):
        self.origin = origin

        self.__output = None

    def lines(self):
        return self.trim().split("\n")

    def trim(self):
        if self.__output is None:
            self.__output = self.origin.stdout.strip()
        return self.__output
