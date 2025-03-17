from ...core import Deployer


def deploy_unlock(dep: Deployer):
    if dep.test("[ -f {{deploy_path}}/.dep/deploy.lock ]"):
        dep.run("rm -f {{deploy_path}}/.dep/deploy.lock")
        dep.info("Deployment process is unlocked.")
    else:
        dep.info("Deployment process has been unblocked before.")
