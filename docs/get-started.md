## Requirements

HapiDeploy requires Python `3.13+`, so you need to check your python version.

```bash
python --version
```

## Installation

You can install the `hapideploy` library using pip.

```bash
pip install hapideploy==0.1.0
```

Check if the `hapi` command is available.

```bash
hapi about
```

If you see a result like this, the installation process is successful.

```plain
Hapi CLI 0.1.0
```

I recommend you to hold HapiDeploy stuff in a directory called ".hapi" inside each project directory. You should also create isolated Python environments for them. Then, you should run the `hapi` command inside `.hapi` directory, so generated resources are going to be separated from your projects.

```bash
cd /path/to/your/project-1

mkdir .hapi

cd .hapi

uv venv --python 3.13

source ./.venv/bin/activate

pip install hapideploy==0.1.0

hapi about

hapi init
```

## Usage

Create files by the `init` command.
```bash
hapi init
```

After that, you can define [remotes](./remotes.md) (at least one) in the `inventory.yml` file.

```yml
remotes:
  remote-1:
    host: 192.168.33.11
    user: vagrant
  remote-2:
    host: 192.168.33.12
    user: vagrant
```

You may define one or more [tasks](./tasks.md) in the `deploy.py` file.

```python
from hapi import Context
from hapi.cli import app

@app.task(name="whoami", desc="Run whoami command")
def whoami(c: Context):
    c.run("whoami")
```

Executing the "whoami" task on all remotes.

```bash
hapi whoami
```

Try "hapi --help" for more information.

```bash
hapi --help
```
