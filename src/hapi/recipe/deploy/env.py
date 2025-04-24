from ...core import Context


def deploy_env(c: Context):
    c.cd("{{release_path}}")

    if c.test("[ -f .env ]"):
        c.info("The .env file already exists ({{release_path}}/.env)")
        return

    if c.test("[ ! -f {{dotenv_example}} ]"):
        c.info(
            "The {{dotenv_example}} file does not exist ({{release_path}}/{{dotenv_example}})"
        )
        return

    c.run("cp {{dotenv_example}} .env")
    c.info("The .env file is created ({{release_path}}/.env)")
