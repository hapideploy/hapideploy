from ...core import Context


def deploy_symlink(c: Context):
    release_path = c.cook("release_path")

    if c.cook("use_atomic_symlink", False):
        c.run("mv -T {{deploy_path}}/release {{current_path}}")
    else:
        # Atomic override symlink.
        c.run("{{bin/symlink}} {{release_path}} {{current_path}}")
        # Remove release link.
        c.run("cd {{deploy_path}} && rm release")

    c.info(f"The current path is symlinked ({release_path})")

    c.put("deployed", c.cook("release_name"))
