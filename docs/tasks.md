A task contains activities you want to do in a specific context.

## Defining a task

In the `deploy.py` file, you can define a task using the `app.task` decorator.

```python
from hapi import Context
from hapi.cli import app

@app.task(name='whoami', desc="Run whoami command")
def whoami(c: Context):
    c.run('whoami')
```

> When you `hapi whoami`, it will run "whoami" on each defined remote in the `inventory.yml` file.

## Grouping tasks

You can group some tasks in one. Let's see the example below. I to define some "deploy:*" tasks before grouping them in one called "deploy".

```python
from hapi.cli import app

app.group(
    name="deploy",
    desc="Deploy your project",
    do=[
        "deploy:start",
        "deploy:setup",
        "deploy:lock",
        # ...
    ]
)
```

**name** and **desc** parameters are required. They are displayed on the console when a task is being executed or for help or for logging.

> When you `hapi deploy`, it will run "deploy:start", "deploy:setup" and "deploy:lock" on each defined remote in the `inventory.yml` file.
