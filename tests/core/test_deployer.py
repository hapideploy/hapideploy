import typer

from hapi import Container, Deployer


def test_constructor():
    deployer = Deployer()

    assert isinstance(deployer, Container)
    assert isinstance(deployer.typer, typer.Typer)
    assert isinstance(deployer.remotes, list)
    assert isinstance(deployer.tasks, dict)
    assert isinstance(deployer.running, dict)
    assert deployer.io is None


def test_it_can_get_and_set_instance():
    deployer = Deployer()

    Deployer.set_instance(deployer)

    assert deployer == Deployer.get_instance()
    assert deployer == Deployer.get_instance()
