from ..core import Context


def bin_git(c: Context):
    return c.which("git")


def bin_symlink(c: Context):
    return "ln -nfs --relative" if c.cook("use_relative_symlink") is True else "ln -nfs"


def target(c: Context):
    if c.check("branch"):
        return c.cook("branch")

    if c.check("tag"):
        return c.cook("tag")

    if c.check("revision"):
        return c.cook("revision")

    return "HEAD"


def release_path(c: Context):
    if c.test("[ -h {{deploy_path}}/release ]"):
        link = c.run("readlink {{deploy_path}}/release").fetch()
        return link if link[0] == "/" else c.parse("{{deploy_path}}" + "/" + link)

    c.stop('The "release_path" ({{deploy_path}}/release) does not exist.')


def releases_log(c: Context):
    import json

    if c.test("[ -f {{deploy_path}}/.dep/releases_log ]") is False:
        return []

    lines = c.run("tail -n 300 {{deploy_path}}/.dep/releases_log").fetch().split("\n")
    releases = []
    for line in lines:
        releases.insert(0, json.loads(line))
    return releases


def releases_list(c: Context):
    if (
        c.test(
            '[ -d {{deploy_path}}/releases ] && [ "$(ls -A {{deploy_path}}/releases)" ]'
        )
        is False
    ):
        return []

    ll = c.run("cd {{deploy_path}}/releases && ls -t -1 -d */").fetch().split("\n")
    ll = list(map(lambda x: x.strip("/"), ll))

    release_items = c.cook("releases_log")

    releases = []

    for candidate in release_items:
        if str(candidate["release_name"]) in ll:
            releases.append(str(candidate["release_name"]))

    return releases
