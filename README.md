HapiDeploy (WIP)

## Requirements

- Python 3.13

## Installation

Create and go to the `.hapi` directory.

```bash
cd /path/to/your/project

mkdir .hapi

cd .hapi
```

Create an isolated Python virtual environment.

```bash
python -m venv .venv
```

Activate the virtual environment above.

```bash
./.venv/Scripts/activate
```

Install the `hapideploy` package via pip.

```bash
pip install hapideploy
```

## Usage

Create `hapirun.py` and `inventory.yml` files.

```bash
hapi init
```

Run the `deploy` command with default selector `all` and stage `dev`.

```bash 
hapi deploy 
```

Run the `deploy` command with explicit selector and custom options.

```bash
hapi deploy all \
    --stage=dev \
    --options=php_version=8.4,node_version=20.18.0
```

## Development

Install Poetry dependency manager

```powershell
pip install poetry
```

Install Python dependencies

```powershell
poetry install
```

Run tests

```bash
poetry run pytest
```

Fix code style

```bash
poetry run black src/ tests/; poetry run isort src/ tests/;
```
