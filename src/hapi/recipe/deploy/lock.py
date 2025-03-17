from ...core import Deployer


def deploy_lock(dep: Deployer):
    import getpass

    user = getpass.getuser()
    locked = dep.run(
        "[ -f {{deploy_path}}/.dep/deploy.lock ] && echo +locked || echo "
        + user
        + " > {{deploy_path}}/.dep/deploy.lock"
    ).fetch()

    if locked == "+locked":
        locked_user = dep.run("cat {{deploy_path}}/.dep/deploy.lock").fetch()
        dep.stop(
            "Deployment process is locked by "
            + locked_user
            + ".\n"
            + 'Execute "deploy:unlock" task to unlock.'
        )

    dep.info("Deployment process is locked by " + user + " (release: {{release_name}})")
