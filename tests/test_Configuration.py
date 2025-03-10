import pytest

from hapi import Configuration, LogicException


def test_it_puts_a_single_value():
    config = Configuration()

    config.put("stage", "production")
    assert config.find("stage") == "production"

    config.put("keep_releases", 5)
    assert config.find("keep_releases") == 5


def test_it_puts_a_list_value():
    config = Configuration()

    names = [
        "James",
        "John",
        "Jane",
    ]

    config.put("names", names)

    assert config.find("names") == names


def test_it_adds_single_values():
    config = Configuration()
    config.put("names", [])

    config.add("names", "James")
    config.add("names", "John")
    assert config.find("names") == ["James", "John"]


def test_it_adds_list_values():
    config = Configuration()
    config.put("names", [])

    config.add("names", ["James", "Jane"])
    config.add("names", ["John", "Doe"])
    assert config.find("names") == ["James", "Jane", "John", "Doe"]


def test_it_adds_values_for_a_non_existing_key():
    config = Configuration()
    assert config.find("names") is None

    config.add("names", "James")
    config.add("names", "John")
    assert config.find("names") == ["James", "John"]


def test_it_raises_a_logic_exception_if_adding_values_for_a_key_is_not_type_of_list():
    config = Configuration()

    config.put("name", "James")

    with pytest.raises(
        LogicException, match='The value associated with "name" is not a list.'
    ):
        config.add("name", "John")


def test_it_gets_all_values():
    config = Configuration()

    config.put("stage", "production")
    config.put("repository", "git@github.com:hapideploy/hapideploy.git")

    assert config.all() == {
        "stage": "production",
        "repository": "git@github.com:hapideploy/hapideploy.git",
    }
