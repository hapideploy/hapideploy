from hapi import RemoteDefinition


def test_it_creates_a_new_instance():
    remote = RemoteDefinition(host="127.0.0.1")

    assert remote.host == "127.0.0.1"
    assert remote.user == "forge"
    assert remote.deploy_dir == "~/deploy/{{stage}}"
    assert remote.label == "127.0.0.1"

    remote = RemoteDefinition(
        host="app-server", user="forge", deploy_dir="~/hapideploy/{{stage}}"
    )

    assert remote.host == "app-server"
    assert remote.user == "forge"
    assert remote.deploy_dir == "~/hapideploy/{{stage}}"
    assert remote.label == "app-server"

    remote = RemoteDefinition(
        host="127.0.0.1",
        user="forge",
        deploy_dir="~/hapideploy/{{stage}}",
        label="localhost",
    )

    assert remote.host == "127.0.0.1"
    assert remote.user == "forge"
    assert remote.deploy_dir == "~/hapideploy/{{stage}}"
    assert remote.label == "localhost"
