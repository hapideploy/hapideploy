from ..core import Deployer, Program


def bootstrap(app: Program):
    return Provider(app)


class Provider:
    def __init__(self, app: Program):
        self.app = app

        self.boot()

    def boot(self):
        self.app.deployer.add_task("deploy", "Run deployment tasks", self.deploy)
        self.app.deployer.add_task(
            "deploy:start", "Start the deployment process", self.deploy_start
        )
        self.app.deployer.add_task(
            "deploy:setup", "Prepare the deployment directory", self.deploy_setup
        )
        self.app.deployer.add_task(
            "deploy:lock", "Lock the deployment process", self.deploy_lock
        )
        self.app.deployer.add_task(
            "deploy:unlock", "Unlock the deployment process", self.deploy_unlock
        )

    def deploy(self, dep: Deployer):
        dep.config.put("current_file", "{{deploy_dir}}/current")

        try:
            dep.run_tasks(
                [
                    "deploy:start",
                    "deploy:setup",
                    "deploy:lock",
                    "deploy:unlock",
                ]
            )
        except RuntimeException:
            dep.run_task("deploy:unlock")

    def deploy_start(self, dep: Deployer):
        release_name = (
            int(dep.cat("{{deploy_dir}}/.dep/latest_release")) + 1
            if dep.test("[ -f {{deploy_dir}}/.dep/latest_release ]")
            else 1
        )

        dep.config.put("release_name", release_name)

        dep.info("Deploying {{name}} to {{stage}} (release {{release_name}})")

    def deploy_setup(self, dep: Deployer):
        command = """[ -d {{deploy_dir}} ] || mkdir -p {{deploy_dir}};
cd {{deploy_dir}};
[ -d .dep ] || mkdir .dep;
[ -d releases ] || mkdir releases;
[ -d shared ] || mkdir shared;"""

        dep.run(command)

        if dep.test("[ ! -L {{current_file}} ] && [ -d {{current_file}} ]"):
            dep.stop(
                "There is a directory (not symlink) at {{current_file}}.\n Remove this directory so it can be replaced with a symlink for atomic deployments."
            )

        dep.info("The {{deploy_dir}} is ready for deployment")

    def deploy_lock(self, dep: Deployer):
        import getpass

        user = getpass.getuser()
        locked = dep.run(
            "[ -f {{deploy_dir}}/.dep/deploy.lock ] && echo +locked || echo "
            + user
            + " > {{deploy_dir}}/.dep/deploy.lock"
        ).fetch()

        if locked == "+locked":
            locked_user = dep.run("cat {{deploy_dir}}/.dep/deploy.lock").fetch()
            dep.stop(
                "Deployment process is locked by "
                + locked_user
                + ".\n"
                + 'Execute "deploy:unlock" task to unlock.'
            )

        dep.run("echo {{release_name}} > {{deploy_dir}}/.dep/latest_release")

        dep.info(
            "Deployment process is locked by "
            + user
            + " (release_name: {{release_name}})"
        )

    def deploy_unlock(self, dep: Deployer):
        dep.run("rm -f {{deploy_dir}}/.dep/deploy.lock")

        dep.info("Deployment process is unlocked.")
