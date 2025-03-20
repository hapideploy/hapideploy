import pytest

from hapi.core import Container


def test_it_can_get_and_set_instance():
    container = Container()

    Container.set_instance(container)

    assert Container.get_instance() == Container.get_instance()


def test_it_puts_a_single_value():
    container = Container()

    container.put("stage", "production")
    assert container.make("stage") == "production"

    container.put("keep_releases", 5)
    assert container.make("keep_releases") == 5


def test_it_puts_a_list_value():
    container = Container()

    names = [
        "James",
        "John",
        "Jane",
    ]

    container.put("names", names)

    assert container.make("names") == names


def test_it_adds_single_values():
    container = Container()
    container.put("names", [])

    container.add("names", "James")
    container.add("names", "John")
    assert container.make("names") == ["James", "John"]


def test_it_adds_list_values():
    container = Container()
    container.put("names", [])

    container.add("names", ["James", "Jane"])
    container.add("names", ["John", "Doe"])
    assert container.make("names") == ["James", "Jane", "John", "Doe"]


def test_it_adds_values_when_key_not_exist():
    container = Container()
    assert not container.has("names")

    container.add("names", "James")
    container.add("names", "John")
    assert container.make("names") == ["James", "John"]


def test_it_raises_a_logic_exception_if_adding_values_when_key_not_a_list():
    container = Container()

    container.put("name", "James")

    with pytest.raises(
        ValueError, match='The value associated with "name" is not a list.'
    ):
        container.add("name", "John")


def test_it_checks_if_a_key_exists():
    container = Container()

    container.put("stage", "production")
    container.bind("releases_list", lambda _: None)

    assert container.has("stage") is True
    assert container.has("releases_list")

    assert container.has("repository") is False


def test_it_binds_a_callback_to_a_key():
    container = Container()

    def bin_php(c: Container):
        return "/usr/bin/php" + c.make("php_version")

    container.put("php_version", "8.4")
    container.bind("bin/php", bin_php)

    assert container.has("bin/php")
    assert container.make("bin/php") == "/usr/bin/php8.4"


def test_it_binds_using_resolve_annotation():
    container = Container()

    @container.resolve(key="languages")
    def resolve_name(_):
        return ["JavaScript", "PHP", "Python", "Go"]

    assert container.has("languages")
    assert container.make("languages") == ["JavaScript", "PHP", "Python", "Go"]


def test_it_returns_fallback_if_key_does_not_exist():
    container = Container()

    value = container.make("message", "message does not exist")

    assert value == "message does not exist"


def test_it_raises_exception_if_key_does_not_exist():
    container = Container()

    with pytest.raises(
        ValueError, match='The key "repository" is not defined in the container.'
    ):
        container.make("repository", throw=True)

    with pytest.raises(ValueError, match="message must be a string"):
        container.make("message", throw=ValueError("message must be a string"))


def test_it_passes_container_to_callback():
    container = Container()

    def bin_php(c: Container):
        return c

    container.bind("bin/php", bin_php)

    assert container.make("bin/php") == container


def test_it_passes_inject_to_callback():
    container = Container()

    def bin_php(inject):
        return inject

    container.bind("bin/php", bin_php)

    exception = Exception()

    assert container.make("bin/php", inject=exception) == exception
