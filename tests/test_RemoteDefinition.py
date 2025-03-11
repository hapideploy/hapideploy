from hapi import RemoteDefinition


def test_it_requires_host_only():
    remote = RemoteDefinition(host="app-server")

    assert remote.host == "app-server"
    assert remote.user == "hapi"
    assert remote.port == 22
    assert remote.deploy_dir == "~/deploy/{{stage}}"
    assert remote.label == "app-server"
    assert remote.id == "hapi@app-server:22"


def test_it_creates_an_instance_with_ip():
    remote = RemoteDefinition(host="192.168.33.11")

    assert remote.host == "192.168.33.11"
    assert remote.id == "hapi@192.168.33.11:22"


def test_it_creates_an_instance_with_hostname():
    remote = RemoteDefinition(host="app-server")

    assert remote.host == "app-server"
    assert remote.id == "hapi@app-server:22"


def test_it_creates_an_instance_with_domain():
    remote = RemoteDefinition(host="hapideploy.com")

    assert remote.host == "hapideploy.com"
    assert remote.id == "hapi@hapideploy.com:22"


def test_it_creates_an_instance_with_user():
    remote = RemoteDefinition(host="192.168.33.11", user="vagrant")

    assert remote.user == "vagrant"
    assert remote.id == "vagrant@192.168.33.11:22"


def test_it_creates_an_instance_with_port():
    remote = RemoteDefinition(host="192.168.33.11", port=2222)

    assert remote.port == 2222
    assert remote.id == "hapi@192.168.33.11:2222"


def test_it_creates_an_instance_with_deploy_dir():
    remote = RemoteDefinition(host="192.168.33.11", deploy_dir="~/custom/{{stage}}")

    assert remote.deploy_dir == "~/custom/{{stage}}"


def test_it_creates_an_instance_with_label():
    remote = RemoteDefinition(host="192.168.33.11", label="custom-server")

    assert remote.label == "custom-server"
