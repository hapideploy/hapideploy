import json
import shlex

from ..core import Deployer, Provider


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

    if dep.test("[ -f {{deploy_dir}}/.dep/releases_log ]") is False:
        return []

    lines = dep.run("tail -n 300 {{deploy_dir}}/.dep/releases_log").fetch().split("\n")
    releases = []
    for line in lines:
        releases.insert(0, json.loads(line))
    return releases


def releases_list(dep: Deployer):
    if (
        dep.test(
            '[ -d {{deploy_dir}}/releases ] && [ "$(ls -A {{deploy_dir}}/releases)" ]'
        )
        is False
    ):
        return []

    ll = dep.run("cd {{deploy_dir}}/releases && ls -t -1 -d */").fetch().split("\n")
    ll = list(map(lambda x: x.strip("/"), ll))

    release_items = dep.make("releases_log")

    releases = []

    for candidate in release_items:
        if str(candidate["release_name"]) in ll:
            releases.append(str(candidate["release_name"]))

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

    if dep.test("[ ! -L {{current_path}} ] && [ -d {{current_path}} ]"):
        dep.stop(
            "There is a directory (not symlink) at {{current_path}}.\n Remove this directory so it can be replaced with a symlink for atomic deployments."
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
            "%s archive %s | tar -x -f - -C {{release_path}} 2>&1"
            % (git, target_with_dir)
        )
    else:
        dep.stop("Unknown `update_code_strategy` option: {{update_code_strategy}}.")

    # Save git revision in REVISION file.
    rev = shlex.quote(dep.run(f"{git} rev-list {dep.make('target')} -1").fetch())
    dep.run("echo " + rev + " > {{release_path}}/REVISION")

    dep.info("Code is updated")


def deploy_env(dep: Deployer):
    dep.cd("{{release_path}}")

    if dep.test("[ ! -e .env ] && [ -f {{dotenv_example}} ]"):
        dep.run("cp {{dotenv_example}} .env")
        dep.info(".env is created")


def deploy_shared(dep: Deployer):
    shared_dir_items = dep.make("shared_dirs", [])

    for a in shared_dir_items:
        for b in shared_dir_items:

            if a != b and (a.rstrip("/") + "/").find(b.rstrip("/") + "/") == 0:
                raise Exception(f"Can not share same directories {a} and {b}")

    shared_path = "{{deploy_dir}}/shared"

    copy_verbosity = "v" if dep.io().debug() else ""

    # Share directories
    for item_dir in shared_dir_items:
        item_dir = item_dir.strip("/")

        if not dep.test(f"[ -d {shared_path}/{item_dir} ]"):
            dep.run(f"mkdir -p {shared_path}/{item_dir}")

            if dep.test("[ -d $(echo {{release_path}}/" + item_dir + ") ]"):
                segments = item_dir.split("/")
                segments.pop()
                dirname = "/".join(segments)
                dep.run(
                    "cp -r"
                    + copy_verbosity
                    + " {{release_path}}/"
                    + item_dir
                    + " "
                    + shared_path
                    + "/"
                    + dirname
                )

        dep.run("rm -rf {{release_path}}/" + item_dir)

        dep.run("mkdir -p `dirname {{release_path}}/" + item_dir + "`")

        dep.run(
            "{{bin/symlink}} %s/%s {{release_path}}/%s"
            % (shared_path, item_dir, item_dir)
        )

    shared_file_items = dep.make("shared_files", [])

    # Share files
    for item_file in shared_file_items:
        segments = dep.parse(item_file).split("/")
        segments.pop()
        dirname = "/".join(segments)

        if not dep.test("[ -d %s/%s ]" % (shared_path, dirname)):
            dep.run(
                "cp -r%s {{release_path}}/%s %s/%s"
                % (copy_verbosity, item_file, shared_path, item_file)
            )

        dep.run(
            "if [ -f $(echo {{release_path}}/%s) ]; then rm -rf {{release_path}}/%s; fi"
            % (item_file, item_file)
        )

        dep.run(
            "if [ ! -d $(echo {{release_path}}/%s) ]; then mkdir -p {{release_path}}/%s;fi"
            % (dirname, dirname)
        )

        dep.run(
            "[ -f %s/%s ] || touch %s/%s"
            % (shared_path, item_file, shared_path, item_file)
        )

        dep.run(
            "{{bin/symlink}} %s/%s {{release_path}}/%s"
            % (shared_path, item_file, item_file)
        )

    dep.info("Shared directories and files.")


class CommonProvider(Provider):
    def register(self):
        self.app.put("dotenv_example", ".env.example")
        self.app.put("current_path", "{{deploy_dir}}/current")
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

        self.app.add_task("deploy:env", "Configure .env file", deploy_env)

        self.app.add_task(
            "deploy:shared",
            "Create symlinks for shared directories and files",
            deploy_shared,
        )

        self.app.add_task("deploy:lock", "Lock the deployment process", deploy_lock)
        self.app.add_task(
            "deploy:unlock", "Unlock the deployment process", deploy_unlock
        )

        self.bind_shared()

        self.bind_writable()

        self.task_deploy_writable()
        self.task_deploy_symlink()
        self.task_deploy_clean()
        self.task_deploy_success()

        self.task_deploy()

    def bind_shared(self):
        self.app.put("shared_dirs", [])
        self.app.put("shared_files", [])

    def bind_writable(self):
        self.app.put("writable_dirs", [])
        self.app.put("writable_mode", "group")
        self.app.put("writable_recursive", True)
        self.app.put("writable_use_sudo", False)
        self.app.put("writable_user", "www-data")
        self.app.put("writable_group", "www-data")

    def task_deploy_writable(self):
        def deploy_writable(dep: Deployer):
            dirs = " ".join(dep.make("writable_dirs", []))

            if dirs.strip() == "":
                return

            if dirs.find(" /") != -1:
                dep.stop(
                    "Absolute path not allowed in config parameter `writable_dirs`."
                )

            dep.cd("{{release_path}}")

            dep.run(f"mkdir -p {dirs}")

            mode = dep.make("writable_mode")  # chown, chgrp or chmod
            recursive = "-R" if dep.make("writable_recursive") is True else ""
            sudo = "sudo" if dep.make("writable_use_sudo") is True else ""

            if mode == "user":
                user = dep.make("writable_user", "www-data")
                dep.run(f"{sudo} chown -L {recursive} {user} {dirs}")
                dep.run(f"{sudo} chmod {recursive} u+rwx {dirs}")
            elif mode == "group":
                group = dep.make("writable_group", "www-data")
                dep.run(f"{sudo} chgrp -L {recursive} {group} {dirs}")
                dep.run(f"{sudo} chmod {recursive} g+rwx {dirs}")
            elif mode == "user:group":
                user = dep.make("writable_user", "www-data")
                group = dep.make("writable_group", "www-data")
                dep.run(f"{sudo} chown -L {recursive} {user}:{group} {dirs}")
                dep.run(f"{sudo} chmod {recursive} u+rwx {dirs}")
                dep.run(f"{sudo} chmod {recursive} g+rwx {dirs}")
            elif mode == "chmod":
                chmod_mode = dep.make("writable_chmod_mode", "0775")
                dep.run(f"{sudo} chmod {recursive} {chmod_mode} {dirs}")
            else:
                dep.stop(f"Unsupported [writable_mode]: {mode}")

            dep.info("Make directories and files writable")

        self.app.add_task(
            "deploy:writable", "Make directories and files writable", deploy_writable
        )

    def task_deploy_symlink(self):
        def deploy_symlink(dep: Deployer):
            current_path = dep.make("current_path")

            if dep.make("use_atomic_symlink", False):
                dep.run("mv -T {{deploy_dir}}/release " + current_path)
            else:
                # Atomic override symlink.
                dep.run(
                    "cd {{deploy_dir}} && {{bin/symlink}} {{release_path}} "
                    + current_path
                )
                # Remove release link.
                dep.run("cd {{deploy_dir}} && rm release")

        self.app.add_task(
            "deploy:symlink", "Creates the symlink to release", deploy_symlink
        )

    def task_deploy_clean(self):
        def deploy_clean(dep: Deployer):
            keep = dep.make("keep_releases", 3)

            dep.run("cd {{deploy_dir}} && if [ -e release ]; then rm release; fi")

            releases = dep.make("releases_list")

            if keep < len(releases):
                sudo = "sudo" if dep.make("clean_use_sudo", False) else ""
                releases = dep.make("releases_list")
                deploy_dir = dep.make("deploy_dir")
                for release_name in releases[keep:]:
                    dep.run(f"{sudo} rm -rf {deploy_dir}/releases/{release_name}")

        self.app.add_task(
            "deploy:clean",
            "Clean deployment process, E.g. remove old release candidates",
            deploy_clean,
        )

    def task_deploy_success(self):
        def deploy_success(dep: Deployer):
            dep.info("Successfully deployed!")

        self.app.add_task(
            "deploy:success",
            "Announce the deployment process is suceed",
            deploy_success,
        )

    def task_deploy(self):
        self.app.add_group(
            "deploy",
            "Run deployment tasks",
            [
                "deploy:start",
                "deploy:setup",
                "deploy:lock",
                "deploy:release",
                "deploy:code",
                "deploy:env",
                "deploy:shared",
                "deploy:writable",
                # custom tasks
                "deploy:symlink",
                "deploy:unlock",
                "deploy:clean",
                "deploy:success",
            ],
        )
