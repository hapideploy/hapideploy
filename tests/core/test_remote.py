from hapi import Container, Remote


def test_it_inherits_container():
    remote = Remote(host="app-server")

    assert isinstance(remote, Container)


def test_it_requires_host_only():
    remote = Remote(host="app-server")

    assert remote.host == "app-server"
    assert remote.user == "hapi"
    assert remote.port == 22
    assert remote.label == "app-server"
    assert remote.key == "hapi@app-server:22"


def test_it_creates_an_instance_with_ip():
    remote = Remote(host="192.168.33.11")

    assert remote.host == "192.168.33.11"
    assert remote.key == "hapi@192.168.33.11:22"


def test_it_creates_an_instance_with_hostname():
    remote = Remote(host="app-server")

    assert remote.host == "app-server"
    assert remote.key == "hapi@app-server:22"


def test_it_creates_an_instance_with_domain():
    remote = Remote(host="hapideploy.com")

    assert remote.host == "hapideploy.com"
    assert remote.key == "hapi@hapideploy.com:22"


def test_it_creates_an_instance_with_user():
    remote = Remote(host="192.168.33.11", user="vagrant")

    assert remote.user == "vagrant"
    assert remote.key == "vagrant@192.168.33.11:22"


def test_it_creates_an_instance_with_port():
    remote = Remote(host="192.168.33.11", port=2222)

    assert remote.port == 2222
    assert remote.key == "hapi@192.168.33.11:2222"


def test_it_creates_an_instance_with_label():
    remote = Remote(host="192.168.33.11", label="custom-server")

    assert remote.label == "custom-server"


def test_it_creates_an_instance_with_pemfile():
    remote = Remote(
        host="192.168.33.11", label="custom-server", pemfile="/path/.ssh/id_ed25519"
    )

    assert remote.pemfile == "/path/.ssh/id_ed25519"
