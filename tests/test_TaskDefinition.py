from hapi import TaskDefinition


def test_constructor():
    def task_func():
        return "Detect the new release name"

    task = TaskDefinition(
        name="deploy:start", desc="Start a new deployment", func=task_func
    )

    assert task.name == "deploy:start"
    assert task.desc == "Start a new deployment"
    assert task.func == task_func

    assert task.func() == task_func()
