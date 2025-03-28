import json

from ...core import Context


def deploy_release(c: Context):
    c.cd("{{deploy_path}}")

    if c.test("[ -h release ]"):
        c.run("rm release")

    releases = c.cook("releases_list")
    release_name = c.cook("release_name")
    release_dir = f"releases/{release_name}"

    if c.test(f"[ -d {release_dir} ]"):
        c.stop(
            f'Release name "{release_name}" already exists.\nIt can be overridden via:\n --options=release_name={release_name}'
        )

    c.run("echo {{release_name}} > .dep/latest_release")

    import time

    timestamp = time.time()
    import getpass

    user = getpass.getuser()

    candidate = {
        "created_at": timestamp,
        "release_name": str(release_name),
        "user": user,
        "target": c.cook("target"),
    }

    json_data = json.dumps(candidate)

    c.run(f"echo '{json_data}' >> .dep/releases_log")

    c.run(f"mkdir -p {release_dir}")

    c.run("{{bin/symlink}} " + release_dir + " {{deploy_path}}/release")

    c.info(
        "The {{deploy_path}}/"
        + release_dir
        + " is created and symlinked (release: {{release_name}})"
    )

    releases.insert(0, release_name)

    if len(releases) >= 2:
        c.put("previous_release", "{{deploy_path}}/releases/" + releases[1])
