import os
from pathlib import Path

from .core.context import Context
from .core.program import Program

app = Program()

app.set_instance(app)


def load_remote(key, data):
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


def load_recipe(name: str):
    if name == "common":
        from .recipe.common import Common
        app.load(Common)
    if name == "express":
        from .recipe.express import Express
        app.load(Express)
    if name == "laravel":
        from .recipe.laravel import Laravel
        app.load(Laravel)


def load_config(app, key, info):
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


def load_task(name: str, body: dict):
    desc: str = str(body.get("desc", ""))
    if "run" in body:

        def func(c: Context):
            for command in body.get("run", []):
                c.run(command)

        app.define_task(name, desc, func)
    elif "do" in body:
        if isinstance(body.get("do"), str):
            app.group(name, desc, str(body.get("do")))
        elif isinstance(body["do"], list):
            resolved: list[str] = []
            for name in body.get("do", []):
                resolved.append((str(name)))
            app.group(name, desc, resolved)


def main():
    inventory_file = os.getcwd() + "/inventory.yml"

    if Path(inventory_file).exists():
        app.discover(inventory_file)

    yaml_file_names = ["hapi.yml", "hapi.yaml"]

    for file_name in yaml_file_names:
        yaml_file = Path(os.getcwd() + "/" + file_name)
        if yaml_file.exists():
            import yaml

            with open(yaml_file) as stream:
                loaded_data = yaml.safe_load(stream)

                if not isinstance(loaded_data, dict):
                    break

                # Load remotes from the hapi.yml file
                if "remotes" in loaded_data:
                    if isinstance(loaded_data.get("remotes"), dict):
                        for key, data in loaded_data["remotes"].items():
                            load_remote(key, data)
                    else:
                        raise ValueError(
                            '"remotes" definition is invalid in hapi.yml file.'
                        )

                # Load recipes from the hapi.yml file
                if "recipes" in loaded_data:
                    if isinstance(loaded_data.get("recipes"), list):
                        for name in loaded_data.get("recipes"):
                            load_recipe(name)
                    else:
                        raise ValueError(
                            '"recipes" definition is invalid in hapi.yml file.'
                        )

                # Load config from the hapi.yml file
                if "config" in loaded_data:
                    if isinstance(loaded_data.get("config"), dict):
                        for key, info in loaded_data.get("config").items():
                            load_config(app, key, info)
                    else:
                        raise ValueError(
                            '"config" definition is invalid in hapi.yml file.'
                        )

                # Load tasks from the hapi.yml file
                if "tasks" in loaded_data:
                    if isinstance(loaded_data.get("tasks"), dict):
                        for name, body in loaded_data.get("tasks").items():
                            load_task(name, body)
                    else:
                        raise ValueError(
                            '"tasks" definition is invalid in hapi.yml file.'
                        )

                # Load before hooks from the hapi.yml file
                if "before" in loaded_data:
                    if isinstance(loaded_data.get("before"), dict):
                        for name, do in loaded_data.get("before").items():
                            app.before(name, do)
                    else:
                        raise ValueError(
                            '"before" definition is invalid in hapi.yml file.'
                        )

                # Load after hooks from the hapi.yml file
                if "after" in loaded_data:
                    if isinstance(loaded_data.get("after"), dict):
                        for name, do in loaded_data.get("after").items():
                            app.after(name, do)
                    else:
                        raise ValueError(
                            '"after" definition is invalid in hapi.yml file.'
                        )

    run_file_names = ["deploy.py"]

    for file_name in run_file_names:
        run_file = Path(os.getcwd() + "/" + file_name)
        if run_file.exists():
            code = Path(run_file).read_text()
            exec(code)
            break

    app.start()
