## Context

Whenever a task is being executed against a remote, it has a context. Here are available activities in a context.

### io()

Get the io (InputOutput) instance.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    if c.io().debug():
        pass # Do something
```

### info()

Print an INFO message.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    c.info('This is an INFO message.')
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

Set a runtime configuration item.

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

Make or resolve a configuration value by its key.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    repository = c.cook('repository')
    branch = c.cook('branch')
    c.info(f"Use {branch} of {repository}")
```

### parse()

Parse a string and inject a configuration value for each replacement surrounded by `{{` and `}}`. It will raise a `MissingConfiguration` exception if there is a non-existing configuration key.

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

Check if running a command on the current remote is successful.

```python
@app.task(name="sample", desc="This is the sample task")
def sample(c: Context):
    if not c.test("[ -d {{deploy_path}} ]"):
        c.info("{{deploy_path}} is a directory.")
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
