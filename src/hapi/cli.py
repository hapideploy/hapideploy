import os
from pathlib import Path

from .toolbox import app


def start():
    inventory_file = os.getcwd() + "/inventory.yml"

    if Path(inventory_file).exists():
        app.discover(inventory_file)

    run_files = [Path(os.getcwd() + "/deploy.py"), Path(os.getcwd() + "/hapirun.py")]

    for run_file in run_files:
        if run_file.exists():
            code = Path(run_file).read_text()
            exec(code)
            break

    app.start()
