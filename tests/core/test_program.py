import os

import pytest

from hapi.core import Deployer, Program, Provider
from hapi.exceptions import InvalidProviderClass


class DummyProvider(Provider):
    def bindings(self) -> list[tuple]:
        return [
            ("release_name", "feature-a"),
            ("bin/python", lambda _: "/usr/bin/python3"),
        ]

    def tasks(self) -> list[tuple]:
        return [
            ("one", "ONE", lambda _: None),
            ("two", "TWO", lambda _: None),
            ("three", "THREE", lambda _: None),
        ]

    def groups(self) -> list[tuple]:
        return [
            ("deploy", "DEPLOY", ["one", "two", "three"]),
        ]


class FoobarProvider:
    pass


def test_it_creates_a_program_instance():
    app = Program()

    assert isinstance(app, Deployer)


def test_it_loads_a_valid_provider():
    app = Program()

    app.load(DummyProvider)

    assert not app.has("name")
    assert app.make("release_name") == "feature-a"
    assert app.make("bin/python", "/usr/bin/python3")

    tasks = app.get_tasks().all()
    assert tasks[0].name == "one"
    assert tasks[0].desc == "ONE"
    assert tasks[1].name == "two"
    assert tasks[1].desc == "TWO"
    assert tasks[2].name == "three"
    assert tasks[2].desc == "THREE"

    group = app.get_tasks().find("deploy")
    assert group.desc == "DEPLOY"
    assert group.children == ["one", "two", "three"]


def test_it_loads_an_invalid_provider():
    app = Program()
    with pytest.raises(
        InvalidProviderClass, match="The given class must be a subclass of Provider"
    ):
        app.load(FoobarProvider)


def test_it_discovers_an_inventory_file():
    app = Program()

    current_dir = os.path.dirname(os.path.realpath(__file__))

    app.discover(current_dir + "/../inventory.yml")

    assert len(app.get_remotes().all()) == 2

    assert app.get_remotes().all()[0].host == "127.0.0.1"
    assert app.get_remotes().all()[0].user == "vagrant"
    assert app.get_remotes().all()[0].port == 2201
    assert app.get_remotes().all()[0].label == "ubuntu-1"
    assert app.get_remotes().all()[0].pemfile == "/path/to/ssh/id_ed25519"
    assert app.get_remotes().all()[0].make("deploy_path") == "~/custom/{{stage}}"

    assert app.get_remotes().all()[1].host == "10.0.0.1"
    assert app.get_remotes().all()[1].label == "ubuntu-2"
