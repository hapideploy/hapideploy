from ...core import Deployer


def deploy_symlink(dep: Deployer):
    current_path = dep.cook("current_path")

    if dep.cook("use_atomic_symlink", False):
        dep.run("mv -T {{deploy_path}}/release " + current_path)
    else:
        # Atomic override symlink.
        dep.run(
            "cd {{deploy_path}} && {{bin/symlink}} {{release_path}} " + current_path
        )
        # Remove release link.
        dep.run("cd {{deploy_path}} && rm release")
