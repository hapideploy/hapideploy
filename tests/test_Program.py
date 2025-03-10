from typer import Typer

from hapi import Deployer, Program


def test_constructor():
    app = Program()

    assert isinstance(app.deployer, Deployer)


def test_the_put_shortcut():
    app = Program()

    app.put("stage", "production")
    app.put("repository", "git@github.com:hapideploy/hapideploy.git")

    # assert app.deployer.config.find('stage') == 'production'

    assert app.deployer.config.all() == dict(
        stage="production", repository="git@github.com:hapideploy/hapideploy.git"
    )


def test_the_add_shortcut():
    app = Program()

    app.add("names", "James")
    app.add("names", ["John", "Jane"])

    assert app.deployer.config.find("names") == ["James", "John", "Jane"]


def test_the_host_shortcut():
    app = Program()

    app.host(name="ubuntu-1", user="vagrant", deploy_dir="~/hapideploy/{{stage}}")
    assert len(app.deployer.remotes) == 1

    remote = app.deployer.remotes[0]
    assert remote.host == "ubuntu-1"
    assert remote.user == "vagrant"
    assert remote.deploy_dir == "~/hapideploy/{{stage}}"
    assert remote.label == "ubuntu-1"
