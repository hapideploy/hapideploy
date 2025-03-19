from ...core import Deployer


def deploy_writable(dep: Deployer):
    dirs = " ".join(dep.cook("writable_dirs", []))

    if dirs.strip() == "":
        return

    if dirs.find(" /") != -1:
        dep.stop("Absolute path not allowed in config parameter `writable_dirs`.")

    dep.cd("{{release_path}}")

    dep.run(f"mkdir -p {dirs}")

    mode = dep.cook("writable_mode")  # chown, chgrp or chmod
    recursive = "-R" if dep.cook("writable_recursive") is True else ""
    sudo = "sudo" if dep.cook("writable_use_sudo") is True else ""

    if mode == "user":
        user = dep.cook("writable_user", "www-data")
        dep.run(f"{sudo} chown -L {recursive} {user} {dirs}")
        dep.run(f"{sudo} chmod {recursive} u+rwx {dirs}")
    elif mode == "group":
        group = dep.cook("writable_group", "www-data")
        dep.run(f"{sudo} chgrp -L {recursive} {group} {dirs}")
        dep.run(f"{sudo} chmod {recursive} g+rwx {dirs}")
    elif mode == "user:group":
        user = dep.cook("writable_user", "www-data")
        group = dep.cook("writable_group", "www-data")
        dep.run(f"{sudo} chown -L {recursive} {user}:{group} {dirs}")
        dep.run(f"{sudo} chmod {recursive} u+rwx {dirs}")
        dep.run(f"{sudo} chmod {recursive} g+rwx {dirs}")
    elif mode == "chmod":
        chmod_mode = dep.cook("writable_chmod_mode", "0775")
        dep.run(f"{sudo} chmod {recursive} {chmod_mode} {dirs}")
    else:
        dep.stop(f"Unsupported [writable_mode]: {mode}")

    dep.info("Make directories and files writable")
