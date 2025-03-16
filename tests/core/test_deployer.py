import pytest

from hapi.core import ArrayInputOutput, Container, Deployer
from hapi.core.io import ConsoleInputOutput
from hapi.core.process import CommandResult, Runner
from hapi.core.remote import Remote
from hapi.exceptions import StoppedException
from hapi.log import BufferStyle, NoneStyle


class DummyResult(CommandResult):
    def __init__(self):
        super().__init__()

    def fetch(self):
        return "+true"


class DummyRunner(Runner):
    def _do_run_command(self, remote: Remote, command: str, **kwargs):
        self.container.add("run", command)
        return DummyResult()


def test_it_creates_a_deployer_instance():
    deployer = Deployer()

    assert isinstance(deployer, Container)
    assert isinstance(deployer.io(), ConsoleInputOutput)
    assert isinstance(deployer.log(), NoneStyle)

    deployer = Deployer(ArrayInputOutput(), BufferStyle())

    assert isinstance(deployer, Container)
    assert isinstance(deployer.io(), ArrayInputOutput)
    assert isinstance(deployer.log(), BufferStyle)


def test_bootstrap():
    deployer = Deployer()

    with pytest.raises(StoppedException):
        deployer.bootstrap(selector="all", stage="dev")


# TODO: Test if it autoload load inventory.yml if it exists.
def test_the_start_method():
    pass


def test_the_add_remote_method():
    deployer = Deployer()

    deployer.add_remote(
        host="ubuntu-1",
        user="vagrant",
        port=2201,
        pemfile="/path/to/pemfile",
    ).put("deploy_path", "~/hapideploy/{{stage}}")
    assert len(deployer.remotes().all()) == 1

    remote = deployer.remotes().all()[0]
    assert remote.host == "ubuntu-1"
    assert remote.user == "vagrant"
    assert remote.port == 2201
    assert remote.label == "ubuntu-1"
    assert remote.make("deploy_path") == "~/hapideploy/{{stage}}"


def test_run_task_method():
    deployer = Deployer(ArrayInputOutput(), NoneStyle())

    def sample(dep: Deployer):
        dep.put("sample", "sample is called.")

    remote = deployer.add_remote(host="127.0.0.1", port=2201, user="vagrant").put(
        "deploy_path", "~/deploy/{{stage}}"
    )

    deployer.add_task("sample", "This is a sample task", sample)

    deployer.put("current_remote", remote)

    deployer.bootstrap(
        runner=DummyRunner(deployer, deployer.tasks(), deployer.io(), deployer.log())
    )

    assert deployer.has("sample") is False
    deployer.run_task("sample")
    assert deployer.make("sample") == "sample is called."
