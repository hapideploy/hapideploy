import os
from pathlib import Path

from .core.context import Context
from .core.program import Program

app = Program()

app.set_instance(app)


def define_remote(key, data):
    if data is None:
        app.remote(host=key, label=key)
    if data.get("host") is None:
        data["host"] = key
    else:
        data["label"] = key

    bindings = data.get("with")

    if bindings is not None:
        del data["with"]

    remote = app.define_remote(**data)

    if isinstance(bindings, dict):
        for k, v in bindings.items():
            remote.put(k, v)


def define_binding(app, key, info):
    if "put" in info:
        app.put(key, info.get("put"))
    elif "add" in info:
        app.put(key, info.get("add"))
    elif "bind" in info:

        def callback(c: Context):
            exec_context = {"c": c, "result": None}
            exec(info.get("bind"), exec_context)
            return exec_context["result"]

        app.bind(key, callback)
    else:
        raise ValueError(f"Invalid configuration for key: {key}")


def main():
    inventory_file = os.getcwd() + "/inventory.yml"

    if Path(inventory_file).exists():
        app.discover(inventory_file)

    hapi_yaml_file = Path(os.getcwd() + "/hapi.yml")

    if hapi_yaml_file.exists():
        import yaml

        with open(hapi_yaml_file) as stream:
            loaded_data = yaml.safe_load(stream)

            # Load remotes from the hapi.yml file
            if isinstance(loaded_data.get("remotes"), dict):
                for key, data in loaded_data["remotes"].items():
                    define_remote(key, data)

            for value in loaded_data.get("recipes"):
                if value == "common":
                    from .recipe.common import Common

                    app.load(Common)
                if value == "laravel":
                    from .recipe.laravel import Laravel

                    app.load(Laravel)

            for key, info in loaded_data.get("config").items():
                define_binding(app, key, info)

            for name, body in loaded_data.get("tasks").items():

                def func(c: Context):
                    for command in body.get("run", []):
                        c.run(command)

                app.define_task(name, body.get("desc"), func)

        app.start()
        return

    run_file_names = ["deploy.py", "hapirun.py"]

    for file_name in run_file_names:
        run_file = Path(os.getcwd() + "/" + file_name)
        if run_file.exists():
            code = Path(run_file).read_text()
            exec(code)
            break

    app.start()
