import pytest

from hapi import Container, LogicException


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


def test_it_adds_values_for_a_non_existing_key():
    container = Container()
    assert container.make("names") is None

    container.add("names", "James")
    container.add("names", "John")
    assert container.make("names") == ["James", "John"]


def test_it_raises_a_logic_exception_if_adding_values_for_a_key_is_not_type_of_list():
    container = Container()

    container.put("name", "James")

    with pytest.raises(
        LogicException, match='The value associated with "name" is not a list.'
    ):
        container.add("name", "John")


def test_it_checks_if_a_key_exists():
    container = Container()

    container.put("stage", "production")

    assert container.has("stage") is True

    assert container.has("repository") is False


def test_it_binds_a_callback_to_a_key():
    container = Container()

    def bin_php(c: Container):
        return "/usr/bin/php" + c.make("php_version")

    container.put("php_version", "8.4")
    container.bind("bin/php", bin_php)

    assert container.has("bin/php")
    assert container.make("bin/php") == "/usr/bin/php8.4"


def test_it_parses_text():
    container = Container()

    container.put("release_name", 1)

    assert (
        container.parse("cd ~/deploy/release/{{release_name}}")
        == "cd ~/deploy/release/1"
    )

    container.put("stage", "production")
    container.put("release_name", "1")
    container.put("release_dir", "~/deploy//{{stage}}/releases/{{release_name}}")
    container.put("bin/python", "/usr/bin/python3")

    parsed = container.parse(
        "cd ~/deploy/releases/{{release_name}} && {{bin/python}} main.py"
    )

    assert parsed == "cd ~/deploy/releases/1 && /usr/bin/python3 main.py"
