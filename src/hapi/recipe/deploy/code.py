import shlex

from ...core import Context


def deploy_code(c: Context):
    git = c.cook("bin/git")
    repository = c.cook("repository")

    bare = c.parse("{{deploy_path}}/.dep/repo")

    env = dict(
        GIT_TERMINAL_PROMPT="0",
        GIT_SSH_COMMAND=c.cook("git_ssh_command"),
    )

    c.run(f"[ -d {bare} ] || mkdir -p {bare}")
    c.run(
        f"[ -f {bare}/HEAD ] || {git} clone --mirror {repository} {bare} 2>&1", env=env
    )

    c.cd(bare)

    # TODO: Check if remote origin url is changed, clone again.
    # if c.run(f"{git} config --get remote.origin.url").fetch() != repository:
    #     c.cd('{{deploy_path}}')
    #     c.run("rm -rf bare")

    c.run(f"{git} remote update 2>&1", env=env)

    target_with_dir = c.cook("target")
    if isinstance(c.cook("sub_directory"), str):
        target_with_dir += ":{{sub_directory}}"

    release_path = c.cook("release_path")

    # TODO: Support clone strategy
    strategy = c.cook("update_code_strategy")
    if strategy == "archive":
        c.run(
            "%s archive %s | tar -x -f - -C %s 2>&1"
            % (git, target_with_dir, release_path)
        )
    else:
        c.stop("Unknown `update_code_strategy` option: {{update_code_strategy}}.")

    # Save git revision in REVISION file.
    rev = shlex.quote(c.run(f"{git} rev-list {c.cook('target')} -1").fetch())
    c.run(f"echo {rev} > {release_path}/REVISION")

    c.info("Code is updated")
