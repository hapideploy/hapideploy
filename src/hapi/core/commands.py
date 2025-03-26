from rich.console import Console
from rich.table import Table

from .container import Binding, Container


class ConfigListCommand:
    def __init__(self, container: Container):
        self.container = container

    def __call__(self, *args, **kwargs):
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


class ConfigShowCommand:
    def __init__(self, container: Container):
        self.container = container

    def __call__(self, *args, **kwargs):
        table = Table("Property", "Detail")

        key = args[0]

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


class TreeCommand:
    def __init__(self, deployer):
        self.__deployer = deployer
        self.__tasks = deployer.tasks()
        self.__io = deployer.io()

        self.__tree = []
        self.__depth = 1

    def __call__(self, task_name: str):
        self.__task_name = task_name

        self._build_tree()

        self._print_tree()

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
        self.__io.writeln("The task-tree for <success>deploy</success>:")

        for item in self.__tree:
            self.__io.writeln(
                "└"
                + ("──" * item["depth"])
                + "> "
                + item["task_name"]
                + " "
                + item["postfix"]
            )
