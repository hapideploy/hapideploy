import json
import shlex

from hapi.exceptions import BindingException

from ..core import Deployer, Program


def bootstrap(app: Program):
    return CommonProvider(app)


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
    if dep.test("[ -h {{deploy_dir}}/release ]"):
        link = dep.run("readlink {{deploy_dir}}/release").fetch()
        return link if link[0] == "/" else dep.make("deploy_dir") + "/" + link

    dep.stop('The "release_path" ({{deploy_dir}}/release) does not exist.')


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


def deploy_start(dep: Deployer):
    release_name = (
        int(dep.cat("{{deploy_dir}}/.dep/latest_release")) + 1
        if dep.test("[ -f {{deploy_dir}}/.dep/latest_release ]")
        else 1
    )

    dep.put("release_name", release_name)

    dep.info("Deploying {{name}} to {{stage}} (release: {{release_name}})")


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

    dep.info(
        "The {{deploy_dir}} directory is ready for deployment (release: {{release_name}})"
    )


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
        "target": dep.make("target"),
    }

    candidate_json = json.dumps(candidate)

    dep.run(f"echo '{candidate_json}' >> .dep/releases_log")

    dep.run(f"mkdir -p {release_dir}")

    dep.run("{{bin/symlink}} " + release_dir + " {{deploy_dir}}/release")

    dep.info(
        "The {{deploy_dir}}/"
        + release_dir
        + " is created and symlinked (release: {{release_name}})"
    )

    releases.insert(0, release_name)

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

    dep.info("Deployment process is locked by " + user + " (release: {{release_name}})")


def deploy_unlock(dep: Deployer):
    dep.run("rm -f {{deploy_dir}}/.dep/deploy.lock")

    dep.info("Deployment process is unlocked.")


def deploy_code(dep: Deployer):
    git = dep.make("bin/git")
    repository = dep.make("repository", throw=True)

    bare = dep.parse("{{deploy_dir}}/.dep/repo")

    env = dict(
        GIT_TERMINAL_PROMPT="0",
        GIT_SSH_COMMAND=dep.make("git_ssh_command"),
    )

    dep.run(f"[ -d {bare} ] || mkdir -p {bare}")
    dep.run(
        f"[ -f {bare}/HEAD ] || {git} clone --mirror {repository} {bare} 2>&1", env=env
    )

    dep.cd(bare)

    # TODO: Check if remote origin url is changed, clone again.
    # if dep.run(f"{git} config --get remote.origin.url").fetch() != repository:
    #     dep.cd('{{deploy_dir}}')
    #     dep.run("rm -rf bare")

    dep.run(f"{git} remote update 2>&1", env=env)

    target_with_dir = dep.make("target")
    if isinstance(dep.make("sub_directory"), str):
        target_with_dir += ":{{sub_directory}}"

    # TODO: Support clone strategy
    strategy = dep.make("update_code_strategy")
    if strategy == "archive":
        dep.run(
            f"{git} archive {target_with_dir} | tar -x -f - -C {release_path(dep)} 2>&1"
        )
    else:
        dep.stop("Unknown `update_code_strategy` option: {{update_code_strategy}}.")

    # Save git revision in REVISION file.
    rev = shlex.quote(dep.run(f"{git} rev-list {dep.make('target')} -1").fetch())
    dep.run("echo " + rev + " > {{release_path}}/REVISION")

    dep.info("Code is updated")


class CommonProvider:
    def __init__(self, app: Program):
        self.app = app

        self.boot()

    def boot(self):
        self.app.put("current_file", "{{deploy_dir}}/current")
        self.app.put("update_code_strategy", "archive")
        self.app.put("git_ssh_command", "ssh -o StrictHostKeyChecking=accept-new")
        self.app.put("sub_directory", False)

        self.app.bind("bin/git", bin_git)
        self.app.bind("bin/symlink", bin_symlink)
        self.app.bind("target", target)
        self.app.bind("release_path", release_path)
        self.app.bind("releases_log", releases_log)
        self.app.bind("releases_list", releases_list)

        self.app.add_task("deploy:start", "Start the deployment process", deploy_start)
        self.app.add_task(
            "deploy:setup", "Prepare the deployment directory", deploy_setup
        )

        self.app.add_task(
            "deploy:release", "Prepare the release candidate", deploy_release
        )

        self.app.add_task("deploy:code", "Update code", deploy_code)

        self.app.add_task("deploy:lock", "Lock the deployment process", deploy_lock)
        self.app.add_task(
            "deploy:unlock", "Unlock the deployment process", deploy_unlock
        )

        self.app.add_group(
            "deploy",
            [
                "deploy:start",
                "deploy:setup",
                "deploy:lock",
                "deploy:release",
                "deploy:code",
                "deploy:unlock",
            ],
            "Run deployment tasks",
        )
