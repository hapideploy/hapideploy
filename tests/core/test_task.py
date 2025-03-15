from hapi.core.task import Task


def test_it_creates_a_task_instance():
    def task_func():
        return "Detect the new release name"

    task = Task(name="deploy:start", desc="Start a new deployment", func=task_func)

    assert task.name == "deploy:start"
    assert task.desc == "Start a new deployment"
    assert task.func == task_func

    assert task.func() == task_func()


# def test_task_bag():
#     tasks = TaskBag()
