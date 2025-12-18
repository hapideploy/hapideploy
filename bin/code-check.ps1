poetry run autoflake --in-place --remove-unused-variables -r src/ tests/

poetry run black src/ tests/

poetry run isort src/ tests/

poetry run mypy src/ tests/ --check-untyped-defs
