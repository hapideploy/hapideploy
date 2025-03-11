from ..core import Deployer, Program


def bootstrap(app: Program):
    return Provider(app)


class Provider:
    def __init__(self, app: Program):
        self.app = app

        self.boot()

    def boot(self):
        @self.app.task(name="deploy:start", desc="Start a new deployment")
        def deploy_start(dep: Deployer):
            dep.config.put("name", "HapiDeploy")

            release_name = (
                dep.cat("{{deploy_dir}}/.dep/latest_release")
                if dep.test("[ -d {{deploy_dir}}/.dep ]")
                else 1
            )

            dep.config.put("release_name", release_name)

            dep.log(
                message=r"Deploying {{name}} to {{stage}} (release {{release_name}})",
                channel="info",
            )
