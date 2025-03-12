HapiDeploy

WIP

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
