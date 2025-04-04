import os
from pathlib import Path

from .toolbox import app


def start():
    hapirun_file = Path(os.getcwd() + "/hapirun.py")

    if hapirun_file.exists():
        code = Path(hapirun_file).read_text()
        exec(code)

    inventory_file = os.getcwd() + "/inventory.yml"

    if Path(inventory_file).exists():
        app.discover(inventory_file)

    app.start()
