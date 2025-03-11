from hapi import Configuration, Deployer


def test_constructor():
    deployer = Deployer()

    assert isinstance(deployer.config, Configuration)
    assert isinstance(deployer.remotes, list)
    assert isinstance(deployer.tasks, list)


def test_it_can_get_and_set_instance():
    deployer = Deployer()

    Deployer.set_instance(deployer)

    assert deployer == Deployer.get_instance()
    assert deployer == Deployer.get_instance()
