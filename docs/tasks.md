A task contains activities you want to do in a specific context.

## Defining a task

You can define a task using the `app.task` decorator.

```python
from hapi import Context
from hapi.cli import app

@app.task(name='whoami', desc="Run whoami on each remote")
def whoami(c: Context):
    c.run('whoami')
```

You can group some tasks in to one. Let's see the example below. You have to define all "deploy:*" tasks before grouping them in to one called "deploy".

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

**name** and **desc** parameters are required. They are displayed on console when a task is being executed or for help or for logging.

## Context

Whenever a task is executed against a remote, it raises a context. Here are available things you can do.

### io()

Get the io (InputOutput) instance.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    if c.io().debug():
        c.io().writeln("Print a debug message")
```

### info()

Print an INFO pretty message.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    c.info('This is an INFO pretty message.')
```

### raise_error()

Raise a context error manually.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    if not c.check('repository'):
        c.raise_error("Missing configuration: repository")
```

### put()

Set a configuration item.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    if not c.cook('release_name'):
        c.put('release_name', 1)
```

### check()

Check a configuration key exists.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    if c.cook('release_name'):
        c.info('release_name is set')
    else:
        c.info('release_name is not set')
```

### cook()

Make/resolve a configuration value.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    repository = c.cook('repository')
    branch = c.cook('branch')
```

### parse()

Parse a string and inject a configuration value for each replacement surrounded by `{{` and `}}`. It may raise MissingConfiguration exceptions if configuration keys don't exist.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    c.put("repository", "https://github.com/hapideploy/hapideploy")
    c.put("deploy_path", "~/deploy")
    
    # The message is "Clone https://github.com/hapideploy/hapideploy into ~/deploy/.dep/repo"
    message = c.parse("Clone {{repository}} to {{deploy_path}}/.dep/repo")
```

### sudo()

Run a sudo command on the current remote.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    c.sudo("apt-get update")
```

### run()

Run a command on the current remote (as the SSH user defined for each remote).

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    c.run("[ -d {{deploy_path}} ] || mkdir {{deploy_path}}")
```

### test()

Check if running a command on the current remote is true.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    if not c.test("[ -d {{deploy_path}} ]"):
        c.run("mkdir {{deploy__path}}")
```

### cat()

Read a file on the current remote and return it's content as a string.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    latest_release_file = c.parse("{{deploy_path}}/.dep/latest_release")
    
    if c.test(f"[ -f {latest_release_file} ]"):
        latest_release_name = c.cat(latest_release_file)
        c.info(f"The latest release is {latest_release_name}.")
    else:
        c.info(f"{latest_release_file} does not exists or is not a file.")
```

### which()

Run the `which` command on the current remote.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    # it may return "/usr/bin/python3"
    return c.which('python3')
```

### cd()

Change directory.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    # It runs "cd ~/deploy/dev && (ls -lh)"
    c.cd("{{deploy_path}}")
    c.run("ls -lh") 
    
    # It runs "cd ~/deploy/dev && cd .dep && (ls -lh)"
    c.cd(".dep")
    c.run("ls -lh")
```
