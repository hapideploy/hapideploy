from hapi import Deployer


def test_it_can_get_and_set_instance():
    instance = Deployer()

    Deployer.set_instance(instance)

    assert instance == Deployer.get_instance()
    assert instance == Deployer.get_instance()
