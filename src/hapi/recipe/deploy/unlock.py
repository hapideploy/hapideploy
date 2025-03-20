from ...core import Context


def deploy_unlock(c: Context):
    if c.test("[ -f {{deploy_path}}/.dep/deploy.lock ]"):
        c.run("rm -f {{deploy_path}}/.dep/deploy.lock")
        c.info("Deployment process is unlocked.")
    else:
        c.info("Deployment process has been unblocked before.")
