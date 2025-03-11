from hapi.core import Deployer, Program


def bootstrap(app: Program):
    return Provider(app)


class Provider:
    def __init__(self, app: Program):
        self.app = app

        self.boot()

    def boot(self):
        @self.app.task(name="deploy:start", desc="Start a new deployment")
        def deploy_start(dep: Deployer):
            name = "HapiDeploy"
            stage = dep.config.find("stage")

            release_name = (
                dep.cat("{{deply_dir}}/.dep/latest_release")
                if dep.test("{{deply_dir}}/.dep/latest_release")
                else 1
            )

            dep.log(
                message=f"Deploying {name} to {stage} (release {release_name})",
                channel="info",
            )
