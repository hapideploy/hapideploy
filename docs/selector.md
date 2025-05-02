Selector is for choosing remotes to interact with. Currently, HapiDeploy only supports selecting remotes by their labels.

## Usage

For example, the `inventory.yaml` file defines 3 remotes like this.

```yaml
remotes:
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

@app.task(name="ping", desc="Check SSH connection")
def ping(c: Context):
    c.run("whoami")
```

Run `hapi ping` or `hapi ping all` will execute the `ping` task on all remotes.

```bash
hapi ping

hapi ping all
```

> The default selector is "all".

If you want to run the `ping` task against the `server-1` only, you have to specify it. It's similar to `server-2` and `server-3`.

```bash
hapi ping server-1
hapi ping server-2
hapi ping server-3
```
