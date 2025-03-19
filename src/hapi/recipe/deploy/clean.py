from ...core import Deployer


def deploy_clean(dep: Deployer):
    keep = dep.cook("keep_releases", 3)

    dep.run("cd {{deploy_path}} && if [ -e release ]; then rm release; fi")

    releases = dep.cook("releases_list")

    if keep < len(releases):
        sudo = "sudo" if dep.cook("clean_use_sudo", False) else ""
        releases = dep.cook("releases_list")
        deploy_path = dep.cook("deploy_path")
        for release_name in releases[keep:]:
            dep.run(f"{sudo} rm -rf {deploy_path}/releases/{release_name}")
