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
