import pytest

from hapi.exceptions import ItemNotFound
from hapi.support import Collection, extract_curly_braces


class Person:
    pass


class Student(Person):
    pass


class Language:
    pass


def test_extract_curly_braces():
    keys = extract_curly_braces("cd {{release_path}} && {{bin/npm}} run install")

    assert keys == ["release_path", "bin/npm"]


def test_collection():
    collection = Collection(Person)

    assert collection.empty()

    with pytest.raises(TypeError):
        collection.add(Language())

    p1 = Person()
    p1.name = "John"
    collection.add(p1)

    assert collection.empty() is False

    p2 = Person()
    p2.name = "Jane"
    collection.add(p2)

    collection.filter_key(lambda name, item: item.name == name)

    assert collection.find("John") == p1
    assert collection.find("Jane") == p2
    assert collection.match(lambda item: item.name == "John") == p1

    with pytest.raises(ItemNotFound):
        collection.find("James")

    with pytest.raises(ItemNotFound):
        collection.match(lambda item: item.name == "James")

    assert collection.all() == [p1, p2]

    # TODO: test filter method
