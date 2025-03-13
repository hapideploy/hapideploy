import os

from hapi import Deployer, Program


def test_constructor():
    app = Program()

    assert isinstance(app, Deployer)


def test_the_host_method():
    app = Program()

    app.host(name="ubuntu-1", user="vagrant", deploy_dir="~/hapideploy/{{stage}}")
    assert len(app.remotes) == 1

    remote = app.remotes[0]
    assert remote.host == "ubuntu-1"
    assert remote.user == "vagrant"
    assert remote.deploy_dir == "~/hapideploy/{{stage}}"
    assert remote.label == "ubuntu-1"


def test_the_load_method():
    app = Program()

    current_dir = os.path.dirname(os.path.realpath(__file__))

    app.load(current_dir + "/../inventory.yml")

    assert len(app.remotes) == 3

    assert app.remotes[0].host == "127.0.0.1"
    assert app.remotes[0].user == "vagrant"
    assert app.remotes[0].port == 2201
    assert app.remotes[0].deploy_dir == "~/custom/{{stage}}"
    assert app.remotes[0].label == "ubuntu-1"
    assert app.remotes[0].pemfile == "/path/to/ssh/id_ed25519"

    assert app.remotes[1].host == "10.0.0.1"
    assert app.remotes[1].label == "ubuntu-2"

    assert app.remotes[2].host == "ubuntu-3"
    assert app.remotes[2].host == "ubuntu-3"
