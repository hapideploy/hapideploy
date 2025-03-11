from hapi import Config, Deployer, Remote


def test_constructor():
    deployer = Deployer()

    assert isinstance(deployer.config, Config)
    assert isinstance(deployer.remotes, list)
    assert isinstance(deployer.tasks, dict)


def test_it_can_get_and_set_instance():
    deployer = Deployer()

    Deployer.set_instance(deployer)

    assert deployer == Deployer.get_instance()
    assert deployer == Deployer.get_instance()


def test_it_can_parse_running_remote_deploy_dir():
    deployer = Deployer()

    deployer.config.put("stage", "production")

    deployer.running_remote = Remote(
        host="127.0.0.1", deploy_dir="~/path/to/deploy/{{stage}}"
    )

    parsed = deployer.parse("cd {{deploy_dir}}")

    assert parsed == "cd ~/path/to/deploy/production"


def test_it_can_parse_any_configuration_keys():
    deployer = Deployer()

    deployer.config.put("stage", "production")
    deployer.config.put("release_name", "1")
    deployer.config.put(
        "release_dir", "/path/to/deploy/{{stage}}/releases/{{release_name}}"
    )
    deployer.config.put("bin/python", "/usr/bin/python3")

    parsed = deployer.parse("cd {{release_dir}} && {{bin/python}} main.py")

    assert (
        parsed == "cd /path/to/deploy/production/releases/1 && /usr/bin/python3 main.py"
    )
