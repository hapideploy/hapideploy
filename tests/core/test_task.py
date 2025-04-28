from hapi.core.task import Task


def test_it_creates_a_task_instance():
    def task_func(_):
        return "Detect the new release name"

    task = Task(name="deploy:start", desc="Start a new deployment", func=task_func)

    assert task.name == "deploy:start"
    assert task.desc == "Start a new deployment"
    assert task.func == task_func

    assert task.func(None) == task_func(None)


# def test_task_bag():
#     tasks = TaskBag()
