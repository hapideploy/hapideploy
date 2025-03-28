import pytest

from hapi.exceptions import ItemNotFound
from hapi.support import Collection, env_stringify, extract_curly_brackets


class Person:
    def __init__(self, name: str):
        self.name = name


class Student(Person):
    pass


class Language:
    def __init__(self, name: str):
        self.name = name


def test_env_stringify_function():
    env = dict(
        LIB_NAME="HapiDeploy",
        LIB_VERSION="1.0.0.dev",
        LIB_DESC="It is a modern deployment tool.",
        LIB_YEAR=2025,
    )

    assert (
        env_stringify(env)
        == "LIB_NAME=HapiDeploy LIB_VERSION=1.0.0.dev LIB_DESC='It is a modern deployment tool.' LIB_YEAR=2025"
    )


def test_extract_curly_brackets():
    keys = extract_curly_brackets("cd {{release_path}} && {{bin/npm}} run install")

    assert keys == ["release_path", "bin/npm"]


def test_collection_add():
    collection = Collection(Person)

    with pytest.raises(TypeError):
        collection.add(Language("Python"))


def test_collection_empty():
    collection = Collection(Person)

    assert collection.empty()

    collection.add(Person("John"))

    assert not collection.empty()


def test_collection_filter_key():
    collection = Collection(Person)

    p1 = Person("John")
    collection.add(p1)

    p2 = Person("Jane")
    collection.add(p2)

    collection.filter_key(lambda name, item: item.name == name)

    with pytest.raises(ItemNotFound):
        collection.find("James")

    with pytest.raises(ItemNotFound):
        collection.match(lambda item: item.name == "James")

    assert collection.find("John") == p1
    assert collection.find("Jane") == p2
    assert collection.match(lambda item: item.name == "John") == p1


def test_collection_filter():
    collection = Collection(Person)

    p1 = Person("John")
    collection.add(p1)

    p2 = Person("Jane")
    collection.add(p2)

    p3 = Student("James")
    collection.add(p3)

    assert collection.all() == [p1, p2, p3]
    assert collection.filter(lambda p: p.name == "John") == [p1]
    assert collection.filter(lambda p: p.name == "John" or p.name == "James") == [
        p1,
        p3,
    ]
