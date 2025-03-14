import os
from pathlib import Path

from .toolbox import app


def start():
    file = os.getcwd() + "/hapirun.py"
    code = Path(file).read_text()
    exec(code)

    if not app.started():
        app.start()
