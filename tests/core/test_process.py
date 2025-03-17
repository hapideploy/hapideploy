import pytest

from hapi import CommandResult
from hapi.core import ArrayInputOutput, Deployer, Printer, Remote, Runner
from hapi.log import NoneStyle


class DummyResult(CommandResult):
    def __init__(self):
        super().__init__()

    def fetch(self):
        return "+true"


class DummyRunner(Runner):
    def _do_run(self, remote: Remote, command: str, **kwargs):
        self.container.add("run", command)
        return DummyResult()


def create_runner() -> DummyRunner:
    container = Deployer()

    container.put("stage", "testing")

    printer = Printer(container.io(), container.log())

    runner = DummyRunner(container, container.tasks(), printer)

    return runner


def test_runner_parse_method():
    runner = create_runner()

    remote = Remote(
        host="127.0.0.1",
        port=2201,
        user="vagrant",
    ).put("deploy_path", "~/deploy/{{stage}}")

    assert runner.parse("{{deploy_path}}", remote) == "~/deploy/testing"


def test_runner_run_method():
    runner = create_runner()

    remote = Remote(
        host="127.0.0.1",
        port=2201,
        user="vagrant",
    ).put("deploy_path", "~/deploy/{{stage}}")

    runner.run(remote, "mkdir -p {{deploy_path}}/.dep")

    assert runner.container.make("run") == ["mkdir -p ~/deploy/testing/.dep"]


def test_runner_test_method():
    runner = create_runner()

    remote = Remote(
        host="127.0.0.1",
        port=2201,
        user="vagrant",
    ).put("deploy_path", "~/deploy/{{stage}}")

    runner.test(remote, "[ ! -d {{deploy_path}}/.dep ]")

    command = runner.container.make("run")[0]

    for choice in Runner.TEST_CHOICES:
        if command == f"if [ ! -d ~/deploy/testing/.dep ]; then echo +{choice}; fi":
            return

    pytest.fail(
        'It must run command a similar to "if [ ! -d ~/deploy/testing/.dep ]; then echo +true; fi"'
    )


def test_runner_cat_method():
    runner = create_runner()

    remote = Remote(host="127.0.0.1", port=2201, user="vagrant").put(
        "deploy_path", "~/deploy/{{stage}}"
    )

    runner.cat(remote, "{{deploy_path}}/.dep/latest_release")

    assert runner.container.make("run") == ["cat ~/deploy/testing/.dep/latest_release"]


def test_runner_remote_cwd():
    runner = create_runner()

    remote = Remote(host="127.0.0.1", port=2201, user="vagrant").put(
        "deploy_path", "~/deploy/{{stage}}"
    )

    remote.put("cwd", "{{deploy_path}}")

    runner.run(remote, "mkdir -p .dep")
    runner.test(remote, "[ ! -d .dep ]")
    runner.cat(remote, ".dep/latest_release")

    run = runner.container.make("run")

    assert run[0] == "cd ~/deploy/testing && (mkdir -p .dep)"

    assert run[2] == "cd ~/deploy/testing && (cat .dep/latest_release)"

    for choice in Runner.TEST_CHOICES:
        if (
            run[1]
            == f"cd ~/deploy/testing && (if [ ! -d .dep ]; then echo +{choice}; fi)"
        ):
            return

    pytest.fail(
        'It must run command a similar to "cd ~/deploy/testing && (if [ ! -d .dep ]; then echo +true; fi"'
    )
