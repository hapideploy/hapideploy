from ...core import Context


def deploy_env(c: Context):
    c.cd("{{release_path}}")

    if c.test("[ ! -f .env ] && [ -f {{dotenv_example}} ]"):
        c.run("cp {{dotenv_example}} .env")
        c.info(".env is created")
