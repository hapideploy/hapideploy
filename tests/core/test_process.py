import pytest

from hapi import CommandResult
from hapi.core import CacheInputOutput, Deployer, Remote, Runner
from hapi.log import NoneStyle


class DummyResult(CommandResult):
    def __init__(self):
        super().__init__()

    def fetch(self):
        return "+true"


class DummyRunner(Runner):
    def _do_run_command(self, remote: Remote, command: str, **kwargs):
        self.deployer.add("run", command)
        return DummyResult()


def test_runner_run_command_method():
    container = Deployer(CacheInputOutput(), NoneStyle())

    container.put("stage", "testing")
    container.put("deploy_dir", "~/deploy/{{stage}}")

    runner = DummyRunner(container)

    remote = Remote(
        host="127.0.0.1", port=2201, user="vagrant", deploy_dir="~/deploy/{{stage}}"
    )

    runner.run_command(remote, "mkdir -p {{deploy_dir}}/.dep")

    assert container.make("run") == ["mkdir -p ~/deploy/testing/.dep"]


def test_runner_run_test_method():
    container = Deployer(CacheInputOutput(), NoneStyle())

    container.put("stage", "testing")
    container.put("deploy_dir", "~/deploy/{{stage}}")

    runner = DummyRunner(container)

    remote = Remote(
        host="127.0.0.1", port=2201, user="vagrant", deploy_dir="~/deploy/{{stage}}"
    )

    runner.run_test(remote, "[ ! -d {{deploy_dir}}/.dep ]")

    command = container.make("run")[0]

    for choice in Runner.TEST_CHOICES:
        if command == f"if [ ! -d ~/deploy/testing/.dep ]; then echo +{choice}; fi":
            return

    pytest.fail(
        'It must run command a similar to "if [ ! -d ~/deploy/testing/.dep ]; then echo +true; fi"'
    )


def test_runner_run_cat_method():
    container = Deployer(CacheInputOutput(), NoneStyle())

    container.put("stage", "testing")
    container.put("deploy_dir", "~/deploy/{{stage}}")

    runner = DummyRunner(container)

    remote = Remote(
        host="127.0.0.1", port=2201, user="vagrant", deploy_dir="~/deploy/{{stage}}"
    )

    runner.run_cat(remote, "{{deploy_dir}}/.dep/latest_release")

    assert container.make("run") == ["cat ~/deploy/testing/.dep/latest_release"]


def test_runner_remote_cwd():
    container = Deployer(CacheInputOutput(), NoneStyle())

    container.put("stage", "testing")
    container.put("deploy_dir", "~/deploy/{{stage}}")

    runner = DummyRunner(container)

    remote = Remote(
        host="127.0.0.1", port=2201, user="vagrant", deploy_dir="~/deploy/{{stage}}"
    )

    remote.put("cwd", "{{deploy_dir}}")

    runner.run_command(remote, "mkdir -p .dep")
    runner.run_test(remote, "[ ! -d .dep ]")
    runner.run_cat(remote, ".dep/latest_release")

    run = container.make("run")

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
