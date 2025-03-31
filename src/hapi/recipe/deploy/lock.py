from ...core import Context
from ...exceptions import GracefulShutdown


def deploy_lock(c: Context):
    import getpass

    deploy_path = c.cook("deploy_path")

    user = getpass.getuser()

    locked = c.run(
        f"[ -f {deploy_path}/.dep/deploy.lock ] && echo +locked || echo {user} > {deploy_path}/.dep/deploy.lock"
    ).fetch()

    if locked == "+locked":
        locked_user = c.run(f"cat {deploy_path}/.dep/deploy.lock").fetch()

        raise GracefulShutdown(
            f'Deployment process is locked by {locked_user}\nExecute "deploy:unlock" task to unlock.'
        )

    release_name = c.cook("release_name")

    c.info(f"Deployment process is locked by {user} (release: {release_name})")
