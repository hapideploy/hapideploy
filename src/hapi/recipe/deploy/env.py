from ...core import Deployer


def deploy_env(dep: Deployer):
    dep.cd("{{release_path}}")

    if dep.test("[ ! -e .env ] && [ -f {{dotenv_example}} ]"):
        dep.run("cp {{dotenv_example}} .env")
        dep.info(".env is created")
