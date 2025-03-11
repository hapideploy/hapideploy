from ..core import Deployer, Program


def bootstrap(app: Program):
    return Provider(app)


class Provider:
    def __init__(self, app: Program):
        self.app = app

        self.boot()

    def boot(self):
        self.add_deploy()
        self.add_deploy_start()
        self.add_deploy_setup()

    def add_deploy(self):
        @self.app.task(name="deploy", desc="Run deployment tasks")
        def deploy_run(dep: Deployer):
            dep.put("current_file", "{{deploy_dir}}/current")

            dep.run_task("deploy:start")
            dep.run_task("deploy:setup")

    def add_deploy_start(self):
        @self.app.task(name="deploy:start", desc="Start a new deployment")
        def deploy_start(dep: Deployer):
            dep.put("name", "HapiDeploy")

            release_name = (
                dep.cat("{{deploy_dir}}/.dep/latest_release")
                if dep.test("[ -f {{deploy_dir}}/.dep/latest_release ]")
                else 1
            )

            dep.put("release_name", release_name)

            dep.log(
                message=r"Deploying {{name}} to {{stage}} (release {{release_name}})",
                channel="info",
            )

    def add_deploy_setup(self):
        @self.app.task(name="deploy:setup", desc="Prepare the deploy directory")
        def deploy_setup(dep: Deployer):
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
