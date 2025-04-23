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

Create `deploy.py` and `inventory.yml` files.

```bash
hapi init
```

Run the `deploy` command with default selector `all` and stage `dev`.

```bash 
hapi deploy 
```

Run the `deploy` command with explicit selector, stage and custom config.

```bash
hapi deploy all \
    --stage=dev \
    --config=python_version=3.13,node_version=20.18.0
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

Fix code style

```bash
poetry run autoflake --in-place --remove-unused-variables -r src/ tests/; poetry run black src/ tests/; poetry run isort src/ tests/;
```

Run static analysis

```bash
poetry run mypy src/ tests/
````

Run all tests

```bash
poetry run pytest
```
