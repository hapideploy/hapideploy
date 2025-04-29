Fork and clone the repository.

```powershell
git clone https://github.com/hapideploy/hapideploy.git
```

Install Python dependencies.

```powershell
poetry install
```
Run static analysis.

```bash
poetry run mypy src/ tests/
````

Fix code style.

```bash
poetry run autoflake --in-place --remove-unused-variables -r src/ tests/;
poetry run black src/ tests/;
poetry run isort src/ tests/;
```

Run all tests.

```bash
poetry run pytest
```
