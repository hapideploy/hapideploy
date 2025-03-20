from ...core import Context


def deploy_clean(c: Context):
    keep = c.cook("keep_releases", 3)

    c.run("cd {{deploy_path}} && if [ -e release ]; then rm release; fi")

    releases = c.cook("releases_list")

    if keep < len(releases):
        sudo = "sudo" if c.cook("clean_use_sudo", False) else ""
        releases = c.cook("releases_list")
        deploy_path = c.cook("deploy_path")
        for release_name in releases[keep:]:
            c.run(f"{sudo} rm -rf {deploy_path}/releases/{release_name}")
