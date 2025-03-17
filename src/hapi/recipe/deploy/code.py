import shlex

from ...core import Deployer
from ..binding import release_path as resolve_release_path


def deploy_code(dep: Deployer):
    git = dep.make("bin/git")
    repository = dep.make("repository", throw=True)

    bare = dep.parse("{{deploy_path}}/.dep/repo")

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
    #     dep.cd('{{deploy_path}}')
    #     dep.run("rm -rf bare")

    dep.run(f"{git} remote update 2>&1", env=env)

    target_with_dir = dep.make("target")
    if isinstance(dep.make("sub_directory"), str):
        target_with_dir += ":{{sub_directory}}"

    release_path = resolve_release_path(dep)

    # TODO: Support clone strategy
    strategy = dep.make("update_code_strategy")
    if strategy == "archive":
        dep.run(
            "%s archive %s | tar -x -f - -C %s 2>&1"
            % (git, target_with_dir, release_path)
        )
    else:
        dep.stop("Unknown `update_code_strategy` option: {{update_code_strategy}}.")

    # Save git revision in REVISION file.
    rev = shlex.quote(dep.run(f"{git} rev-list {dep.make('target')} -1").fetch())
    dep.run(f"echo {rev} > {release_path}/REVISION")

    dep.info("Code is updated")
