from ...core import Deployer


def deploy_setup(dep: Deployer):
    dep.run("[ -d {{deploy_path}} ] || mkdir -p {{deploy_path}}")
    dep.cd("{{deploy_path}}")
    dep.run("[ -d .dep ] || mkdir .dep")
    dep.run("[ -d releases ] || mkdir releases")
    dep.run("[ -d shared ] || mkdir shared")

    if dep.test("[ ! -L {{current_path}} ] && [ -d {{current_path}} ]"):
        dep.stop(
            "There is a directory (not symlink) at {{current_path}}.\n Remove this directory so it can be replaced with a symlink for atomic deployments."
        )

    dep.info(
        "The {{deploy_path}} directory is ready for deployment (release: {{release_name}})"
    )
