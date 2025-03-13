import os
from pathlib import Path

def start():
    file = os.getcwd() + '/hapirun.py'
    code = Path(file).read_text()
    exec(code)
