import pytest

from hapi import Container
from hapi.core import (
    ArrayInputOutput,
    CommandResult,
    Context,
    Printer,
    Remote,
)
from hapi.core.task import TaskBag
from hapi.log import NoneStyle


class DummyResult(CommandResult):
    def __init__(self):
        super().__init__()

    def fetch(self):
        return "+true"


class DummyContext(Context):
    def _do_run(self, command: str, **kwargs):
        self.container.add("run", command)
        return DummyResult()


def create_context() -> DummyContext:
    container = Container()

    container.put("stage", "testing")

    printer = Printer(ArrayInputOutput(), NoneStyle())

    remote = Remote(
        host="127.0.0.1",
        port=2201,
        user="vagrant",
    ).put("deploy_path", "~/deploy/{{stage}}")

    context = DummyContext(container, remote, TaskBag(), printer)

    return context


def test_context_parse_method():
    context = create_context()

    assert context.parse("{{deploy_path}}") == "~/deploy/testing"


def test_context_run_method():
    context = create_context()

    context.run("mkdir -p {{deploy_path}}/.dep")

    assert context.container.make("run") == ["mkdir -p ~/deploy/testing/.dep"]


def test_context_test_method():
    context = create_context()

    context.test("[ ! -d {{deploy_path}}/.dep ]")

    command = context.container.make("run")[0]

    for choice in Context.TEST_CHOICES:
        if command == f"if [ ! -d ~/deploy/testing/.dep ]; then echo +{choice}; fi":
            return

    pytest.fail(
        'It must run command a similar to "if [ ! -d ~/deploy/testing/.dep ]; then echo +true; fi"'
    )


def test_context_cat_method():
    context = create_context()

    context.cat("{{deploy_path}}/.dep/latest_release")

    assert context.container.make("run") == ["cat ~/deploy/testing/.dep/latest_release"]


def test_context_which_method():
    context = create_context()

    context.which("php")

    assert context.container.make("run") == ["which php"]


def test_context_remote_cwd():
    context = create_context()

    context.cd("{{deploy_path}}")

    context.run("mkdir -p .dep")
    context.test("[ ! -d .dep ]")
    context.cat(".dep/latest_release")

    run = context.container.make("run")

    assert run[0] == "cd ~/deploy/testing && (mkdir -p .dep)"

    assert run[2] == "cd ~/deploy/testing && (cat .dep/latest_release)"

    for choice in Context.TEST_CHOICES:
        if (
            run[1]
            == f"cd ~/deploy/testing && (if [ ! -d .dep ]; then echo +{choice}; fi)"
        ):
            return

    pytest.fail(
        'It must run command a similar to "cd ~/deploy/testing && (if [ ! -d .dep ]; then echo +true; fi"'
    )
