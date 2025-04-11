import pytest

from hapi.collect import Collection
from hapi.exceptions import ItemNotFound


class Person:
    def __init__(self, name: str):
        self.name = name


class Student(Person):
    pass


class Language:
    def __init__(self, name: str):
        self.name = name


def test_collection_add():
    collection = Collection(Person)

    with pytest.raises(TypeError):
        collection.add(Language("Python"))


def test_collection_empty():
    collection = Collection(Person)

    assert collection.empty()

    collection.add(Person("John"))

    assert not collection.empty()


def test_collection_find():
    collection = Collection(Person)

    collection.find_using(lambda name, p: p.name == name)

    p1 = Person("John")
    collection.add(p1)

    p2 = Person("Jane")
    collection.add(p2)

    with pytest.raises(ItemNotFound):
        collection.find("James")

    assert collection.find("John") == p1
    assert collection.find("Jane") == p2


def test_collection_match():
    collection = Collection(Person)

    collection.find_using(lambda name, p: p.name == name)

    p1 = Person("John")
    collection.add(p1)

    p2 = Person("Jane")
    collection.add(p2)

    with pytest.raises(ItemNotFound):
        collection.match(lambda p: p.name == "James")

    assert collection.match(lambda p: p.name == "John") == p1


def test_collection_filter():
    collection = Collection(Person)

    p1 = Person("John")
    collection.add(p1)

    p2 = Person("Jane")
    collection.add(p2)

    p3 = Student("James")
    collection.add(p3)

    assert collection.filter(lambda p: p.name == "John") == [p1]
    assert collection.filter(lambda p: p.name == "John" or p.name == "James") == [
        p1,
        p3,
    ]


def test_collection_all():
    collection = Collection(Person)

    p1 = Person("John")
    collection.add(p1)

    p2 = Person("Jane")
    collection.add(p2)

    p3 = Student("James")
    collection.add(p3)

    assert collection.all() == [p1, p2, p3]
