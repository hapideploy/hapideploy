---
title: Selector
---

Selector is for choosing remotes to interact with. Currently, HapiDeploy only supports selecting remotes by their labels.

## Usage

Run the command below to exec a task against one, some or all remotes.

```bash
hapi <task> [selector]
```

For example, the `inventory.yaml` file defines 3 remotes like this.

```yaml
hosts:
  server-1:
    host: 192.168.33.11
  server-2:
    host: 192.168.33.12
  server-3:
    host: 192.168.33.13
```

The `deploy.py` file defines a task called `ping` like this.

```python
from hapi import Context
from hapi.cli import app

@app.task(name="ping", desc="Check SSH connection to each remote")
def ping(c: Context):
    c.run("whoami")
```

Run `hapi ping` will execute the `ping` task on all remotes.

```bash
hapi ping

hapi ping all
```

If you want to run the `ping` task against the `server-1` only, you have to specify it.

```bash
hapi ping server-1
```
