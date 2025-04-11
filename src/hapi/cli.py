import os
from pathlib import Path

from .core.program import Program

app = Program()

app.set_instance(app)


def main():
    inventory_file = os.getcwd() + "/inventory.yml"

    if Path(inventory_file).exists():
        app.discover(inventory_file)

    run_file_names = ["deploy.py", "hapirun.py"]

    for file_name in run_file_names:
        run_file = Path(os.getcwd() + "/" + file_name)
        if run_file.exists():
            code = Path(run_file).read_text()
            exec(code)
            break

    app.start()
