from ...core import Deployer


def deploy_start(dep: Deployer):
    release_name = (
        int(dep.cat("{{deploy_path}}/.dep/latest_release")) + 1
        if dep.test("[ -f {{deploy_path}}/.dep/latest_release ]")
        else 1
    )

    dep.put("release_name", release_name)

    dep.info("Deploying {{name}} to {{stage}} (release: {{release_name}})")
