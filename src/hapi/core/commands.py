import os
from pathlib import Path
from typing import Annotated, Callable

from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer, prompt

from ..__version import __version__
from .container import BindingCallback, BindingValue, Container
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
        raise NotImplementedError

    def execute(self):
        exit_code = self.handle()
        if isinstance(exit_code, int):
            exit(exit_code)
        exit(0)

    def handle(self):
        raise NotImplementedError


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
        def handler(
            force: Annotated[
                bool, Option(help="Force to create deploy.py and inventory files")
            ] = False,
        ):
            self.io.set_option("force", force)
            self.handle()

    def handle(self):
        if self.io.get_option("force") is False:
            for file in [
                "deploy.py",
                "inventory.yml",
            ]:
                if Path(os.getcwd() + "/" + file).exists():
                    self.io.error(
                        f"{file} already exists. Use --force to overwrite it."
                    )
                    return

        candidates: list[tuple[str, Callable]] = [
            ("blank", InitCommand.deploy_blank),
            ("laravel", InitCommand.deploy_laravel),
            ("express", InitCommand.deploy_express),
        ]

        self.io.writeln("")

        for idx, (name, _) in enumerate(candidates):
            self.io.writeln(f"[<comment>{idx}</comment>] {name}")

        picked = None

        choice = prompt(self.io.decorate("\n<primary>Select a hapi recipe</primary>"))

        for idx, (name, resolve_deploy_file_content) in enumerate(candidates):
            if choice == str(idx) or choice == name:
                picked = idx
                deploy_file_content = resolve_deploy_file_content()
                f = open(os.getcwd() + "/deploy.py", "w")
                f.write(deploy_file_content)
                f.close()
                break

        if picked is None:
            self.io.error(f"Recipe {choice} is invalid.")
            return

        inventory_file_content = """remotes:
  server-1:
    host: 192.168.33.10
    port: 22 # Optional
    user: vagrant # Optional
    identity_file: ~/.ssh/id_ed25519 # Optional
    with:
      deploy_path: ~/deploy/{{stage}}
"""

        f = open(os.getcwd() + "/inventory.yml", "w")
        f.write(inventory_file_content)
        f.close()

        self.io.success("deploy.py and inventory.yml files are created")

    @staticmethod
    def deploy_blank() -> str:
        return """from hapi import Context
from hapi.cli import app

app.put("name", "blank")

@app.task(name="whoami", desc="Run whoami command")
def whoami(c: Context):
    c.run("whoami")
"""

    @staticmethod
    def deploy_laravel() -> str:
        return """from hapi.cli import app
from hapi.recipe import Laravel

app.load(Laravel)

app.put("name", "laravel")
app.put("repository", "https://github.com/hapideploy/laravel")
app.put("branch", "main")

app.add("shared_dirs", [])
app.add("shared_files", [])
app.add("writable_dirs", [])
"""

    @staticmethod
    def deploy_express() -> str:
        return """from hapi.cli import app
from hapi.recipe import Express

app.load(Express)

app.put("name", "express")
app.put("repository", "https://github.com/hapideploy/express")
app.put("branch", "main")

app.add("shared_dirs", [])
app.add("shared_files", [])
app.add("writable_dirs", [])
"""


class ConfigListCommand(Command):
    def define_for(self, console: Typer):
        @console.command(
            name="config:list", help="Display all pre-defined configuration items"
        )
        def handler():
            self.handle()

    def handle(self):
        table = Table("Key", "Kind", "Datatype", "Value")

        bindings = self.container.all()

        value_keys = []
        callback_keys = []

        for key, binding in bindings.items():
            if isinstance(binding, BindingValue):
                value_keys.append(key)
            elif isinstance(binding, BindingCallback):
                callback_keys.append(key)

        value_keys.sort()
        callback_keys.sort()

        for key in callback_keys:
            table.add_row(key, "callback", "-----", "-----")

        for key in value_keys:
            binding = bindings[key]

            value = binding.value
            value_type = type(value).__name__

            if isinstance(value, list):
                value = ", ".join(binding.value)

            table.add_row(
                key,
                "value",
                value_type,
                str(value),
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
        table.add_row(
            "Kind", "value" if isinstance(binding, BindingValue) else "callback"
        )

        if isinstance(binding, BindingValue):
            table.add_row("Datatype", type(binding.value).__name__)
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
        table = Table("Label", "Host", "User", "Port", "IdentityFile")

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
                str(remote.identity_file),
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
