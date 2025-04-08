import os

import typer
from rich.console import Console
from rich.table import Table

from ..__version import __version__
from .container import Binding, Container
from .io import InputOutput
from .task import TaskBag


class AboutCommand:
    NAME = "about"
    DESC = "Display the Hapi CLI information"

    def __init__(self, io: InputOutput):
        self.io = io

    def execute(self) -> int:
        self.io.writeln(f"Hapi CLI <success>{__version__}</success>")

        return 0


class InitCommand:
    NAME = "init"
    DESC = "Initialize hapi files"

    def __init__(self, io: InputOutput):
        self.io = io

    def execute(self) -> int:
        recipe_list = [
            ("1", "laravel"),
        ]

        for key, name in recipe_list:
            self.io.writeln(f" [<comment>{key}</comment>] {name}")

        recipe_name = None

        choice = typer.prompt(
            self.io.decorate("<primary>Select a hapi recipe</primary>")
        )

        for key, name in recipe_list:
            if choice == key or choice == name:
                recipe_name = name

        if not recipe_name:
            self.io.error(f'Value "{choice}" is invalid.')

            return 1

        hapirun_contents = """from hapi.toolbox import app

from hapi.recipe.laravel import Laravel

app.load(Laravel)

app.put("name", "Laravel")
app.put("repository", "https://github.com/laravel/laravel")
app.put("branch", "main")

app.add("shared_dirs", [])
app.add("shared_files", [])
app.add("writable_dirs", [])

if __name__ == "__main__":
    app.start()
"""

        f = open(os.getcwd() + "/hapirun.py", "w")
        f.write(hapirun_contents)
        f.close()

        self.io.success("hapirun.py file is created")

        inventory_contents = """hosts:
  app-server:
    host: 192.168.33.10
    port: 22 # Optional
    user: vagrant # Optional
    pemfile: ~/.ssh/id_ed25519 # Optional
    with:
      deploy_path: ~/deploy/{{stage}}
"""

        f = open(os.getcwd() + "/inventory.yml", "w")
        f.write(inventory_contents)
        f.close()

        self.io.success("inventory.yml file is created")

        return 0


class ConfigListCommand:
    NAME = "config:list"
    DESC = "Display all pre-defined configuration items"

    def __init__(self, container: Container):
        self.container = container

    def execute(self) -> int:
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

        return 0


class ConfigShowCommand:
    NAME = "config:show"
    DESC = "Display details for a configuration item"

    def __init__(self, container: Container, io: InputOutput):
        self.container = container
        self.io = io

    def execute(self) -> int:
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

        return 0


class TreeCommand:
    NAME = "tree"
    DESC = "Display the task-tree for a given task"

    def __init__(self, tasks: TaskBag, io: InputOutput):
        self.__task_name = None
        self.__tasks = tasks
        self.__io = io

        self.__tree = []
        self.__depth = 1

    def execute(self) -> int:
        self.__task_name = self.__io.get_argument("task")

        self._build_tree()

        self._print_tree()

        return 0

    def _build_tree(self):
        self._create_tree_from_task_name(self.__task_name)

    def _create_tree_from_task_name(self, task_name: str, postfix: str = ""):
        task = self.__tasks.find(task_name)

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
        self.__io.writeln("The task-tree for <primary>deploy</primary>:")

        for item in self.__tree:
            self.__io.writeln(
                "└"
                + ("──" * item["depth"])
                + "> "
                + "<primary>"
                + item["task_name"]
                + "</primary>"
                + " "
                + item["postfix"]
            )
