class NoneStyle:
    def __init__(self):
        pass

    def do_write(self, text: str, newline: bool = False):
        pass

    def parse(self, text: str = ""):
        pass

    def write(self, text: str = ""):
        self.do_write(text, False)

    def writeln(self, text: str = ""):
        self.do_write(text, True)
