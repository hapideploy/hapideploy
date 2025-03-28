import shlex

from ...core import Context


def deploy_code(c: Context):
    git = c.cook("bin/git")
    repository = c.cook("repository")
    target = c.cook("target")

    bare = c.parse("{{deploy_path}}/.dep/repo")

    env = dict(
        GIT_TERMINAL_PROMPT="0",
        GIT_SSH_COMMAND=c.cook("git_ssh_command"),
    )

    def update_repo():
        c.run(f"[ -d {bare} ] || mkdir -p {bare}")
        c.run(
            f"[ -f {bare}/HEAD ] || {git} clone --mirror {repository} {bare} 2>&1",
            env=env,
        )

    update_repo()

    if (
        c.run(f"cd {bare} && {git} config --get remote.origin.url").fetch()
        != repository
    ):
        c.run(f"rm -rf {bare}")
        update_repo()

    c.cd(bare)

    c.run(f"{git} remote update 2>&1", env=env)

    target_with_dir = c.cook("target")
    if isinstance(c.cook("sub_directory"), str):
        target_with_dir += ":{{sub_directory}}"

    release_path = c.cook("release_path")

    strategy = c.cook("update_code_strategy")  # archive or clone
    if strategy == "archive":
        c.run(
            "%s archive %s | tar -x -f - -C %s 2>&1"
            % (git, target_with_dir, release_path)
        )
    elif strategy == "clone":
        c.cd(release_path)
        c.run(f"{git} clone -l {bare} .")
        c.run(f"{git} remote set-url origin {repository}", env=env)
        c.run(f"{git} checkout --force {target}")
    else:
        c.stop(f"Unknown `update_code_strategy` option: {strategy}.")

    # Save git revision in REVISION file.
    rev = shlex.quote(c.run(f"{git} rev-list {target} -1").fetch())
    c.run(f"echo {rev} > {release_path}/REVISION")

    c.info("Code is updated")
