from hapi.core import Container, Remote, RemoteBag


def test_it_inherits_container():
    remote = Remote(host="app-server")

    assert isinstance(remote, Container)


def test_it_requires_host_only():
    remote = Remote(host="app-server")

    assert remote.host == "app-server"
    assert remote.user is None
    assert remote.port is None
    assert remote.label == "app-server"
    assert remote.key == "app-server"


def test_it_creates_an_instance_with_ip():
    remote = Remote(host="192.168.33.11")

    assert remote.host == "192.168.33.11"
    assert remote.key == "192.168.33.11"


def test_it_creates_an_instance_with_hostname():
    remote = Remote(host="app-server")

    assert remote.host == "app-server"
    assert remote.key == "app-server"


def test_it_creates_an_instance_with_domain():
    remote = Remote(host="hapideploy.com")

    assert remote.host == "hapideploy.com"
    assert remote.key == "hapideploy.com"


def test_it_creates_an_instance_with_user():
    remote = Remote(host="192.168.33.11", user="vagrant")

    assert remote.user == "vagrant"
    assert remote.key == "vagrant@192.168.33.11"


def test_it_creates_an_instance_with_port():
    remote = Remote(host="192.168.33.11", port=2222)

    assert remote.port == 2222
    assert remote.key == "192.168.33.11:2222"


def test_it_creates_an_instance_with_label():
    remote = Remote(host="192.168.33.11", label="custom-server")

    assert remote.label == "custom-server"


def test_it_creates_an_instance_with_identity_file():
    remote = Remote(
        host="192.168.33.11",
        label="custom-server",
        identity_file="/path/.ssh/id_ed25519",
    )

    assert remote.identity_file == "/path/.ssh/id_ed25519"


def test_it_creates_an_instance_with_passphrase():
    remote = Remote(
        host="192.168.33.11",
        label="test-server",
        passphrase='secret_string'
    )

    assert remote.passphrase == "secret_string"


def test_it_selects_remotes():
    remotes = RemoteBag()

    r1 = Remote(host="192.168.33.11", label="server-1")
    remotes.add(r1)
    r2 = Remote(host="192.168.33.12", label="server-2")
    remotes.add(r2)
    r3 = Remote(host="192.168.33.13", label="server-3")
    remotes.add(r3)

    assert remotes.select("server-1") == [r1]
    assert remotes.select("server-2") == [r2]
    assert remotes.select("server-3") == [r3]

    assert remotes.select("all") == [r1, r2, r3]
