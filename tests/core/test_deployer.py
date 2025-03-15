import pytest

from hapi.core import CacheInputOutput, Container, Deployer
from hapi.core.io import ConsoleInputOutput
from hapi.exceptions import StoppedException
from hapi.log import BufferStyle, NoneStyle


def test_it_creates_a_deployer_instance():
    deployer = Deployer()

    assert isinstance(deployer, Container)
    assert isinstance(deployer.io, ConsoleInputOutput)
    assert isinstance(deployer.log, NoneStyle)

    deployer = Deployer(CacheInputOutput(), BufferStyle())

    assert isinstance(deployer, Container)
    assert isinstance(deployer.io, CacheInputOutput)
    assert isinstance(deployer.log, BufferStyle)


def test_bootstrap():
    deployer = Deployer()

    with pytest.raises(StoppedException):
        deployer._bootstrap(selector="all", stage="dev")


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
        deploy_dir="~/hapideploy/{{stage}}",
    )
    assert len(deployer.remotes().all()) == 1

    remote = deployer.remotes().all()[0]
    assert remote.host == "ubuntu-1"
    assert remote.user == "vagrant"
    assert remote.port == 2201
    assert remote.label == "ubuntu-1"
    assert remote.deploy_dir == "~/hapideploy/{{stage}}"
