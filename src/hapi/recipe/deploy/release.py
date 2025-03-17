import json

from ...core import Deployer


def deploy_release(dep: Deployer):
    dep.cd("{{deploy_path}}")

    if dep.test("[ -h release ]"):
        dep.run("rm release")

    releases = dep.make("releases_list")
    release_name = dep.make("release_name")
    release_dir = f"releases/{release_name}"

    if dep.test(f"[ -d {release_dir} ]"):
        dep.stop(
            f'Release name "{release_name}" already exists.\nIt can be overridden via:\n -o release_name={release_name}'
        )

    dep.run("echo {{release_name}} > .dep/latest_release")

    import time

    timestamp = time.time()
    import getpass

    user = getpass.getuser()

    candidate = {
        "created_at": timestamp,
        "release_name": str(release_name),
        "user": user,
        "target": dep.make("target"),
    }

    json_data = json.dumps(candidate)

    dep.run(f"echo '{json_data}' >> .dep/releases_log")

    dep.run(f"mkdir -p {release_dir}")

    dep.run("{{bin/symlink}} " + release_dir + " {{deploy_path}}/release")

    dep.info(
        "The {{deploy_path}}/"
        + release_dir
        + " is created and symlinked (release: {{release_name}})"
    )

    releases.insert(0, release_name)

    if len(releases) >= 2:
        dep.put("previous_release", "{{deploy_path}}/releases/" + releases[1])
