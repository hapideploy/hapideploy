from ..core import Deployer


def bin_git(_: Deployer):
    return "/usr/bin/git"


def bin_symlink(dep: Deployer):
    return (
        "ln -nfs --relative" if dep.make("use_relative_symlink") is True else "ln -nfs"
    )


def target(dep: Deployer):
    branch = dep.make("branch")
    if branch:
        return branch

    # TODO: Needs to support tag or revision?

    return "HEAD"


def release_path(dep: Deployer):
    if dep.test("[ -h {{deploy_path}}/release ]"):
        link = dep.run("readlink {{deploy_path}}/release").fetch()
        return link if link[0] == "/" else dep.parse("{{deploy_path}}" + "/" + link)

    dep.stop('The "release_path" ({{deploy_path}}/release) does not exist.')


def releases_log(dep: Deployer):
    import json

    if dep.test("[ -f {{deploy_path}}/.dep/releases_log ]") is False:
        return []

    lines = dep.run("tail -n 300 {{deploy_path}}/.dep/releases_log").fetch().split("\n")
    releases = []
    for line in lines:
        releases.insert(0, json.loads(line))
    return releases


def releases_list(dep: Deployer):
    if (
        dep.test(
            '[ -d {{deploy_path}}/releases ] && [ "$(ls -A {{deploy_path}}/releases)" ]'
        )
        is False
    ):
        return []

    ll = dep.run("cd {{deploy_path}}/releases && ls -t -1 -d */").fetch().split("\n")
    ll = list(map(lambda x: x.strip("/"), ll))

    release_items = dep.make("releases_log")

    releases = []

    for candidate in release_items:
        if str(candidate["release_name"]) in ll:
            releases.append(str(candidate["release_name"]))

    return releases
