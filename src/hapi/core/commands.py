import os

from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer, prompt

from ..__version import __version__
from .container import Binding, Container
from .io import InputOutput
from .remote import RemoteBag
from .task import TaskBag


class Command:
    def __init__(
        self, container: Container, io: InputOutput, remotes: RemoteBag, tasks: TaskBag
    ):
        self.container = container
        self.io = io
        self.remotes = remotes
        self.tasks = tasks

    def define_for(self, console: Typer):
        raise NotImplemented

    def execute(self):
        exit_code = self.handle()
        if isinstance(exit_code, int):
            exit(exit_code)
        exit(0)

    def handle(self):
        raise NotImplemented


class AboutCommand(Command):
    def define_for(self, console: Typer):
        @console.command(name="about", help="Display the Hapi CLI information")
        def handler():
            self.execute()

    def handle(self):
        self.io.writeln(f"Hapi CLI <success>{__version__}</success>")


class InitCommand(Command):
    def define_for(self, console: Typer):
        @console.command(name="init", help="Initialize Hapi files")
        def handler():
            self.handle()

    def handle(self):
        recipe_list = [
            ("1", "laravel"),
        ]

        for key, name in recipe_list:
            self.io.writeln(f" [<comment>{key}</comment>] {name}")

        recipe_name = None

        choice = prompt(self.io.decorate("<primary>Select a hapi recipe</primary>"))

        for key, name in recipe_list:
            if choice == key or choice == name:
                recipe_name = name

        if not recipe_name:
            self.io.error(f'Value "{choice}" is invalid.')

        deploy_file_content = """from hapi.cli import app
from hapi.recipe import Laravel

app.load(Laravel)

app.put("name", "laravel")
app.put("repository", "https://github.com/hapideploy/laravel")
app.put("branch", "main")

app.add("shared_dirs", [])
app.add("shared_files", [])
app.add("writable_dirs", [])
"""

        f = open(os.getcwd() + "/deploy.py", "w")
        f.write(deploy_file_content)
        f.close()

        self.io.success("deploy.py file is created")

        inventory_file_content = """hosts:
  app-server:
    host: 192.168.33.10
    port: 22 # Optional
    user: vagrant # Optional
    pemfile: ~/.ssh/id_ed25519 # Optional
    with:
      deploy_path: ~/deploy/{{stage}}
"""

        f = open(os.getcwd() + "/inventory.yml", "w")
        f.write(inventory_file_content)
        f.close()

        self.io.success("inventory.yml file is created")


class ConfigListCommand(Command):
    def define_for(self, console: Typer):
        @console.command(
            name="config:list", help="Display all pre-defined configuration items"
        )
        def handler():
            self.handle()

    def handle(self):
        table = Table("Key", "Kind", "Type", "Value")

        bindings = self.container.all()

        keys = list(bindings.keys())
        keys.sort()

        for key in keys:
            binding = bindings[key]
            value = str(binding.value) if binding.kind == Binding.INSTANT else "-----"

            if isinstance(binding.value, list):
                value = "\n - ".join(binding.value)

                if value != "":
                    value = f" - {value}"

            table.add_row(
                key,
                binding.kind,
                (
                    type(binding.value).__name__
                    if binding.kind == Binding.INSTANT
                    else "-----"
                ),
                value,
            )

        console = Console()
        console.print(table)


class ConfigShowCommand(Command):
    def define_for(self, console: Typer):
        @console.command(
            name="config:show", help="Display details for a configuration item"
        )
        def handler(key: str = Argument(help="A configuration key")):
            self.io.set_argument("key", key)
            self.handle()

    def handle(self):
        table = Table("Property", "Detail")

        key = self.io.get_argument("key")

        bindings = self.container.all()

        binding = bindings[key]

        value = str(binding.value)

        if isinstance(binding.value, list):
            value = "\n - ".join(binding.value)

            if value != "":
                value = f" - {value}"

        table.add_row("Key", key)
        table.add_row("Kind", binding.kind)

        if binding.kind == Binding.INSTANT:
            table.add_row("Type", type(binding.value).__name__)
            table.add_row("Value", value)

        console = Console()
        console.print(table)


class RemoteListCommand(Command):
    def define_for(self, console: Typer):
        @console.command(
            name="remote:list", help="Display a listing of defined remotes"
        )
        def handler(
            selector: str = Argument(
                default=RemoteBag.SELECTOR_ALL, help="The remote selector"
            )
        ):
            self.io.set_argument("selector", selector)

            self.handle()

    def handle(self) -> int:
        table = Table("Label", "Host", "User", "Port", "Pemfile")

        selector = self.io.get_argument("selector")

        selected = self.remotes.select(selector)

        if len(selected) == 0:
            self.io.error(f"No remotes match the selector: {selector}")
            return 1

        for remote in selected:
            table.add_row(
                remote.label,
                remote.host,
                str(remote.user),
                str(remote.port),
                str(remote.pemfile),
            )

        console = Console()
        console.print(table)

        return 0


class TreeCommand(Command):
    NAME = "tree"
    DESC = "Display the task-tree for a given task"

    def __init__(
        self, container: Container, io: InputOutput, remotes: RemoteBag, tasks: TaskBag
    ):
        super().__init__(container, io, remotes, tasks)

        self.__tree: list[dict] = []
        self.__depth: int = 1

    def define_for(self, console: Typer):
        @console.command(name="tree", help="Display the task-tree for a given task")
        def handler(name: str = Argument(help="Name of task to display the tree for")):
            self.io.set_argument("name", name)
            self.handle()

    def handle(self) -> int:
        self._build_tree()

        self._print_tree()

        return 0

    def _build_tree(self):
        self._create_tree_from_task_name(self.io.get_argument("name"))

    def _create_tree_from_task_name(self, task_name: str, postfix: str = ""):
        task = self.tasks.find(task_name)

        if task.before:
            for before_task in task.before:
                self._create_tree_from_task_name(
                    before_task, postfix="// before {}".format(task_name)
                )

        self.__tree.append(
            dict(
                task_name=task.name,
                depth=self.__depth,
                postfix=postfix,
            )
        )

        if task.children:
            self.__depth += 1

            for child in task.children:
                self._create_tree_from_task_name(child, "")

            self.__depth -= 1

        if task.after:
            for after_task in task.after:
                self._create_tree_from_task_name(
                    after_task, postfix="// after {}".format(task_name)
                )

    def _print_tree(self):
        self.io.writeln(
            f"The task-tree for <primary>{self.io.get_argument('name')}</primary>:"
        )

        for item in self.__tree:
            self.io.writeln(
                "└"
                + ("──" * item["depth"])
                + "> "
                + "<primary>"
                + item["task_name"]
                + "</primary>"
                + " "
                + item["postfix"]
            )
