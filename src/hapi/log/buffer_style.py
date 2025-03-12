from .none_style import NoneStyle


class BufferStyle(NoneStyle):
    def __init__(self):
        super().__init__()

        self.buffered = ""

    def do_write(self, text: str = "", newline: bool = False):
        self.buffered += text + ("\n" if newline else "")

    def fetch(self) -> str:
        fetched = self.buffered
        self.buffered = ""
        return fetched
