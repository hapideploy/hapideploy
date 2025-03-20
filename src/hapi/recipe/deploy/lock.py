from ...core import Context


def deploy_lock(c: Context):
    import getpass

    user = getpass.getuser()
    locked = c.run(
        "[ -f {{deploy_path}}/.dep/deploy.lock ] && echo +locked || echo "
        + user
        + " > {{deploy_path}}/.dep/deploy.lock"
    ).fetch()

    if locked == "+locked":
        locked_user = c.run("cat {{deploy_path}}/.dep/deploy.lock").fetch()
        c.stop(
            "Deployment process is locked by "
            + locked_user
            + ".\n"
            + 'Execute "deploy:unlock" task to unlock.'
        )

    c.info("Deployment process is locked by " + user + " (release: {{release_name}})")
