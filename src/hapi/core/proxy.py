from typer import Typer

from ..log import NoneStyle
from .container import Container
from .io import ConsoleInputOutput
from .process import Printer, Runner
from .remote import RemoteBag
from .task import TaskBag


class Proxy:
    def __init__(self, container: Container):
        self.container = container
        self.typer = Typer()

        self.io = ConsoleInputOutput()
        self.log = NoneStyle()

        self.remotes = RemoteBag()
        self.tasks = TaskBag()

        self.selected = []

        self.current_remote = None
        self.current_task = None

        self.prepared = False
        self.started = False

    def runner(self):
        return Runner(self.container, self.tasks, Printer(self.io, self.log))
