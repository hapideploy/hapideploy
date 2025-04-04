import pytest

from hapi.core import Deployer, Remote, Task
from hapi.exceptions import InvalidHookKind, TaskNotFound


def test_it_adds_remotes():
    deployer = Deployer()

    r1 = deployer.define_remote(
        host="192.168.33.11",
        user="vagrant",
        port=22,
        pemfile="~/.ssh/id_rsa",
        label="server-1",
    )

    assert isinstance(r1, Remote)

    assert r1.host == "192.168.33.11"
    assert r1.user == "vagrant"
    assert r1.port == 22
    assert r1.pemfile == "~/.ssh/id_rsa"
    assert r1.label == "server-1"
    assert r1.key == "vagrant@192.168.33.11:22"

    assert deployer.get_remotes().all() == [r1]

    r2 = deployer.define_remote(
        host="192.168.33.12",
        user="vagrant",
        port=22,
        pemfile="~/.ssh/id_rsa",
        label="server-2",
    )

    assert isinstance(r2, Remote)

    assert deployer.get_remotes().all() == [r1, r2]


def test_it_can_not_add_duplicate_remotes():
    deployer = Deployer()

    deployer.define_remote(
        host="192.168.33.11",
        user="vagrant",
        port=22,
        pemfile="~/.ssh/id_rsa",
        label="server-1",
    )

    with pytest.raises(
        ValueError, match='Remote "vagrant@192.168.33.11:22" already exists.'
    ):
        deployer.define_remote(
            host="192.168.33.11",
            user="vagrant",
            port=22,
            pemfile="~/.ssh/id_rsa",
            label="server-1",
        )


def test_it_adds_tasks():
    deployer = Deployer()

    def func_one(_):
        return "func_one"

    t1 = deployer.define_task("one", "ONE", func_one)

    assert isinstance(t1, Task)

    assert t1.name == "one"
    assert t1.desc == "ONE"
    assert t1.func == func_one

    def func_two(_):
        return "func_two"

    t2 = deployer.define_task("two", "TWO", func_two)

    assert isinstance(t2, Task)

    assert t2.name == "two"
    assert t2.desc == "TWO"
    assert t2.func == func_two


def test_it_overrides_task_desc_and_func():
    deployer = Deployer()

    def func_one(_):
        return "func_one"

    def func_two(_):
        return "func_two"

    t1 = deployer.define_task("sample", "ONE", func_one)
    t2 = deployer.define_task("sample", "TWO", func_two)

    assert t2 == t1

    assert t2.name == "sample"
    assert t2.desc == "TWO"
    assert t2.func == func_two

    assert deployer.get_tasks().all() == [t2]


def test_it_adds_groups():
    deployer = Deployer()

    deployer.define_task("one", "ONE", lambda _: None)
    deployer.define_task("two", "TWO", lambda _: None)
    deployer.define_task("three", "THREE", lambda _: None)

    task = deployer.define_group("one-two", "ONE-TWO", ["one", "two"])

    assert task.name == "one-two"
    assert task.desc == "ONE-TWO"
    assert task.children == ["one", "two"]

    task = deployer.define_group("two-three", "TWO-THREE", ["two", "three"])

    assert task.name == "two-three"
    assert task.desc == "TWO-THREE"
    assert task.children == ["two", "three"]


def test_it_can_not_add_groups_contain_undefined_tasks():
    deployer = Deployer()

    t1 = deployer.define_task("one", "ONE", lambda _: None)
    t2 = deployer.define_task("two", "TWO", lambda _: None)

    with pytest.raises(TaskNotFound, match=f'Task "three" is not found.'):
        deployer.define_group("one-two-three", "ONE-TWO-THREE", ["one", "two", "three"])

    assert deployer.get_tasks().all() == [t1, t2]


def test_it_adds_hooks():
    deployer = Deployer()

    deployer.define_task("one", "ONE", lambda _: None)
    deployer.define_task("two", "TWO", lambda _: None)
    deployer.define_task("three", "THREE", lambda _: None)

    task = deployer.define_task("deploy", "DEPLOY", lambda _: None)

    deployer.define_hook(Task.HOOK_BEFORE, "deploy", ["one"])
    deployer.define_hook(Task.HOOK_AFTER, "deploy", ["two"])
    deployer.define_hook(Task.HOOK_FAILED, "deploy", ["three"])

    assert task.before == ["one"]
    assert task.after == ["two"]
    assert task.failed == ["three"]


def test_it_can_not_add_hooks_with_invalid_tasks_or_kinds():
    deployer = Deployer()

    with pytest.raises(TaskNotFound, match='Task "deploy" is not found.'):
        deployer.define_hook(Task.HOOK_BEFORE, "deploy", ["one"])

    deployer.define_task("deploy", "DEPLOY", lambda _: None)

    with pytest.raises(TaskNotFound, match='Task "one" is not found.'):
        deployer.define_hook(Task.HOOK_BEFORE, "deploy", ["one"])

    deployer.define_task("one", "DEPLOY", lambda _: None)

    with pytest.raises(InvalidHookKind):
        deployer.define_hook("invalid", "deploy", ["one"])
