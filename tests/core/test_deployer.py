import os

import pytest
import typer

from hapi import Container, Deployer
from hapi.exceptions import StoppedException


def test_constructor():
    deployer = Deployer()

    assert isinstance(deployer, Container)
    assert isinstance(deployer.typer, typer.Typer)
    assert isinstance(deployer.remotes, list)
    assert isinstance(deployer.tasks, dict)
    assert isinstance(deployer.running, dict)
    assert deployer.io is None


def test_bootstrap():
    deployer = Deployer()

    with pytest.raises(StoppedException):
        deployer.bootstrap(selector="all", stage="dev")


# TODO: Test if it autoload load inventory.yml if it exists.
def test_the_start_method():
    pass


def test_the_host_method():
    deployer = Deployer()

    deployer.host(name="ubuntu-1", user="vagrant", deploy_dir="~/hapideploy/{{stage}}")
    assert len(deployer.remotes) == 1

    remote = deployer.remotes[0]
    assert remote.host == "ubuntu-1"
    assert remote.user == "vagrant"
    assert remote.deploy_dir == "~/hapideploy/{{stage}}"
    assert remote.label == "ubuntu-1"


def test_the_discover_method():
    deployer = Deployer()

    current_dir = os.path.dirname(os.path.realpath(__file__))

    deployer.discover(current_dir + "/../inventory.yml")

    assert len(deployer.remotes) == 2

    assert deployer.remotes[0].host == "127.0.0.1"
    assert deployer.remotes[0].user == "vagrant"
    assert deployer.remotes[0].port == 2201
    assert deployer.remotes[0].deploy_dir == "~/custom/{{stage}}"
    assert deployer.remotes[0].label == "ubuntu-1"
    assert deployer.remotes[0].pemfile == "/path/to/ssh/id_ed25519"

    assert deployer.remotes[1].host == "10.0.0.1"
    assert deployer.remotes[1].label == "ubuntu-2"
