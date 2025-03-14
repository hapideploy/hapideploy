import pytest

from hapi import Container, Deployer
from hapi.exceptions import StoppedException


def test_it_creates_a_deployer_instance():
    deployer = Deployer()

    assert isinstance(deployer, Container)
    assert isinstance(deployer.remotes, list)
    assert isinstance(deployer.tasks, dict)
    assert deployer.io is None


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
    assert len(deployer.remotes) == 1

    remote = deployer.remotes[0]
    assert remote.host == "ubuntu-1"
    assert remote.user == "vagrant"
    assert remote.port == 2201
    assert remote.label == "ubuntu-1"
    assert remote.deploy_dir == "~/hapideploy/{{stage}}"
