from hapi import Deployer, Program


def test_constructor():
    app = Program()

    assert isinstance(app, Deployer)
