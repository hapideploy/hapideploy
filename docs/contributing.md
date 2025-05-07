1. Fork and clone the repository.

    ```bash
    git clone https://github.com/<username>/hapideploy.git
    ```

2. Install Python dependencies.

    ```bash
    poetry install
    ```

3. Create a new branch from `main` and make some changes.

    ```bash
   git checkout -b feature-a
   ```

4. Run static analysis.

    ```bash
    poetry run mypy src/ tests/ --check-untyped-defs
    ````

5. Fix code style.
    
    ```bash
    poetry run autoflake --in-place --remove-unused-variables -r src/ tests/;
    poetry run black src/ tests/;
    poetry run isort src/ tests/;
    ```

6. Run all tests.

    ```bash
    poetry run pytest
    ```

7. Create a pull request into `main.`
