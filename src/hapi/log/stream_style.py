from .none_style import NoneStyle


class StreamStyle(NoneStyle):
    def do_write(self, text: str, newline: bool = False):
        parsed = self.parse(text)
        print(parsed, end="\n" if newline else "")

    def parse(self, text: str = ""):
        return text.replace("<success>", "").replace("</success>", "")

    def write(self, text: str = ""):
        self.do_write(text, False)

    def writeln(self, text: str = ""):
        self.do_write(text, True)
