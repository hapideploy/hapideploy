import pytest

from hapi.core import (
    ArrayInputOutput,
    Container,
    Context,
    Printer,
    Remote,
)
from hapi.core.context import RunResult
from hapi.core.task import TaskBag
from hapi.exceptions import ConfigurationError, ContextError
from hapi.log import NoneStyle


class DummyResult(RunResult):
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


def test_context_io_method():
    context = create_context()

    assert isinstance(context.io(), ArrayInputOutput)


def test_context_exec_method():
    # Check before exec and after exec
    assert True


def test_context_put_method():
    context = create_context()

    context.put("message", "calling context.put in runtime")

    assert context.cook("message") == "calling context.put in runtime"


def test_context_check_method():
    context = create_context()

    assert context.check("stage") is True
    assert context.check("deploy_path") is True
    assert context.check("release_name") is False


def test_context_cook_method():
    context = create_context()

    assert context.cook("stage") == "testing"
    assert context.cook("deploy_path") == "~/deploy/{{stage}}"
    assert context.cook("release_name", "feature-a") == "feature-a"

    with pytest.raises(ConfigurationError, match="Missing configuration: release_name"):
        context.cook("release_name", throw=True)


def test_context_parse_method():
    context = create_context()

    assert context.parse("{{deploy_path}}") == "~/deploy/testing"

    with pytest.raises(ConfigurationError, match="Missing configuration: release_name"):
        context.parse("mkdir {{deploy_path}}/releases/{{release_name}}")

    context.put("release_name", "feature-a")

    assert (
        context.parse("mkdir {{deploy_path}}/releases/{{release_name}}")
        == "mkdir ~/deploy/testing/releases/feature-a"
    )


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


def test_context_cd_method():
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


def test_context_info_method():
    context = create_context()

    info_items = []

    class DummyPrinter(Printer):
        def print_info(self, remote: Remote, message: str):
            info_items.append((remote, message))

    context.printer = DummyPrinter(context.printer.io, context.printer.log)

    context.put("name", "HapiDeploy")

    # printer.print_info will be called with the remote and parsed message.
    context.info("Deploying {{name}} to {{stage}}")

    r, m = info_items[0]

    assert r == context.remote
    assert m == "Deploying HapiDeploy to testing"


def test_context_raise_error_method():
    context = create_context()

    context.put("name", "HapiDeploy")

    with pytest.raises(
        ContextError,
        match="Deploying HapiDeploy to testing has failed due to a system error.",
    ):
        context.raise_error(
            "Deploying {{name}} to {{stage}} has failed due to a system error."
        )
