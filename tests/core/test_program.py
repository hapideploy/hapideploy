import os

import pytest

from hapi.core import Deployer, Program, Provider
from hapi.exceptions import InvalidProviderClass


class DummyProvider(Provider):
    def register(self):
        self.app.put("message", "register DummyProvider")


class FoobarProvider:
    pass


def test_it_creates_a_program_instance():
    app = Program()

    assert isinstance(app, Deployer)


def test_it_loads_a_valid_provider():
    app = Program()

    assert not app.has("message")

    app.load(DummyProvider)

    assert app.has("message")
    assert app.make("message") == "register DummyProvider"


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
    assert app.get_remotes().all()[0].identity_file == "/path/to/ssh/id_ed25519"
    assert app.get_remotes().all()[0].make("deploy_path") == "~/custom/{{stage}}"

    assert app.get_remotes().all()[1].host == "10.0.0.1"
    assert app.get_remotes().all()[1].label == "ubuntu-2"
