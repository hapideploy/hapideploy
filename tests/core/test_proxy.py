from hapi.core import Container, Proxy


def test_it_creates_a_proxy_instance():
    proxy = Proxy(Container())

    assert isinstance(proxy.container, Container)
