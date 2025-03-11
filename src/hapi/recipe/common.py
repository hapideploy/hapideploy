import json

from ..core import Deployer, Program
from ..exceptions import StoppedException


def bootstrap(app: Program):
    return CommonProvider(app)


def bin_symlink(dep: Deployer):
    return (
        "ln -nfs --relative" if dep.make("use_relative_symlink") is True else "ln -nfs"
    )


def releases_log(dep: Deployer):
    import json

    dep.cd("{{deploy_dir}}")

    if dep.test("[ -f .dep/releases_log ]") is False:
        return []

    lines = dep.run("tail -n 300 .dep/releases_log").fetch().split("\n")
    releases = []
    for line in lines:
        releases.insert(0, json.loads(line))
    return releases


def releases_list(dep: Deployer):
    dep.cd("{{deploy_dir}}")

    if dep.test('[ -d releases ] && [ "$(ls -A releases)" ]') is False:
        return []

    ll = dep.run("cd releases && ls -t -1 -d */").fetch().split("\n")
    ll = list(map(lambda x: x.strip("/"), ll))

    release_items = dep.make("releases_log")

    releases = []

    for candidate in release_items:
        if candidate["release_name"] in ll:
            releases.append(candidate["release_name"])

    return releases


def deploy(dep: Deployer):
    dep.put("current_file", "{{deploy_dir}}/current")

    try:
        dep.run_tasks(
            [
                "deploy:start",
                "deploy:setup",
                "deploy:lock",
                "deploy:release",
                "deploy:unlock",
            ]
        )
    except StoppedException:
        # TODO: dep.run_task('deploy:failed')
        dep.run_task("deploy:unlock")


def deploy_start(dep: Deployer):
    release_name = (
        int(dep.cat("{{deploy_dir}}/.dep/latest_release")) + 1
        if dep.test("[ -f {{deploy_dir}}/.dep/latest_release ]")
        else 1
    )

    dep.put("release_name", release_name)

    dep.info("Deploying {{name}} to {{stage}} (release {{release_name}})")


def deploy_setup(dep: Deployer):
    command = """[ -d {{deploy_dir}} ] || mkdir -p {{deploy_dir}};
cd {{deploy_dir}};
[ -d .dep ] || mkdir .dep;
[ -d releases ] || mkdir releases;
[ -d shared ] || mkdir shared;"""

    dep.run(command)

    if dep.test("[ ! -L {{current_file}} ] && [ -d {{current_file}} ]"):
        dep.stop(
            "There is a directory (not symlink) at {{current_file}}.\n Remove this directory so it can be replaced with a symlink for atomic deployments."
        )

    dep.info("The {{deploy_dir}} is ready for deployment")


def deploy_release(dep: Deployer):
    dep.cd("{{deploy_dir}}")

    if dep.test("[ -h release ]"):
        dep.run("rm release")

    releases = dep.make("releases_list")
    release_name = dep.make("release_name")
    release_dir = f"releases/{release_name}"

    if dep.test(f"[ -d {release_dir} ]"):
        dep.stop(
            f'Release name "{release_name}" already exists.\nIt can be overridden via:\n -o release_name={release_name}'
        )

    dep.run("echo {{release_name}} > {{deploy_dir}}/.dep/latest_release")

    import time

    timestamp = time.time()
    import getpass

    user = getpass.getuser()

    candidate = {
        "created_at": timestamp,
        "release_name": release_name,
        "user": user,
        "target": dep.make("branch"),
    }

    candidate_json = json.dumps(candidate)

    dep.run(f"echo '{candidate_json}' >> .dep/releases_log")

    dep.run(f"mkdir -p {release_dir}")

    dep.run("{{bin/symlink}} " + release_dir + " {{deploy_dir}}/release")

    releases.insert(0, release_name)
    dep.bind("releases_list", releases)

    if len(releases) >= 2:
        dep.bind("previous_release", "{{deploy_dir}}/releases/" + releases[1])


def deploy_lock(dep: Deployer):
    import getpass

    user = getpass.getuser()
    locked = dep.run(
        "[ -f {{deploy_dir}}/.dep/deploy.lock ] && echo +locked || echo "
        + user
        + " > {{deploy_dir}}/.dep/deploy.lock"
    ).fetch()

    if locked == "+locked":
        locked_user = dep.run("cat {{deploy_dir}}/.dep/deploy.lock").fetch()
        dep.stop(
            "Deployment process is locked by "
            + locked_user
            + ".\n"
            + 'Execute "deploy:unlock" task to unlock.'
        )

    dep.info(
        "Deployment process is locked by " + user + " (release_name: {{release_name}})"
    )


def deploy_unlock(dep: Deployer):
    dep.run("rm -f {{deploy_dir}}/.dep/deploy.lock")

    dep.info("Deployment process is unlocked.")


class CommonProvider:
    def __init__(self, app: Program):
        self.app = app

        self.boot()

    def boot(self):
        self.app.bind("bin/symlink", bin_symlink)
        self.app.bind("releases_log", releases_log)
        self.app.bind("releases_list", releases_list)

        self.app.add_task("deploy", "Run deployment tasks", deploy)
        self.app.add_task("deploy:start", "Start the deployment process", deploy_start)
        self.app.add_task(
            "deploy:setup", "Prepare the deployment directory", deploy_setup
        )

        self.app.add_task(
            "deploy:release", "Prepare the release candidate", deploy_release
        )

        self.app.add_task("deploy:lock", "Lock the deployment process", deploy_lock)
        self.app.add_task(
            "deploy:unlock", "Unlock the deployment process", deploy_unlock
        )
