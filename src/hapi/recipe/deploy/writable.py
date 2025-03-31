from ...core import Context


def deploy_writable(c: Context):
    dirs = " ".join(c.cook("writable_dirs", []))

    if dirs.strip() == "":
        return

    if dirs.find(" /") != -1:
        c.stop("Absolute path not allowed in config parameter `writable_dirs`.")

    c.cd("{{release_path}}")

    c.run(f"mkdir -p {dirs}")

    mode = c.cook("writable_mode", "chmod")  # chown, chgrp or chmod
    recursive = "-R" if c.cook("writable_recursive") is True else ""
    sudo = "sudo" if c.cook("writable_use_sudo") is True else ""

    if mode == "user":
        user = c.cook("writable_user", "www-data")
        c.run(f"{sudo} chown -L {recursive} {user} {dirs}")
        c.run(f"{sudo} chmod {recursive} u+rwx {dirs}")
    elif mode == "group":
        group = c.cook("writable_group", "www-data")
        c.run(f"{sudo} chgrp -L {recursive} {group} {dirs}")
        c.run(f"{sudo} chmod {recursive} g+rwx {dirs}")
    elif mode == "user:group":
        user = c.cook("writable_user", "www-data")
        group = c.cook("writable_group", "www-data")
        c.run(f"{sudo} chown -L {recursive} {user}:{group} {dirs}")
        c.run(f"{sudo} chmod {recursive} u+rwx {dirs}")
        c.run(f"{sudo} chmod {recursive} g+rwx {dirs}")
    elif mode == "chmod":
        chmod_mode = c.cook("writable_chmod_mode", "0775")
        c.run(f"{sudo} chmod {recursive} {chmod_mode} {dirs}")
    else:
        c.stop(f"Unsupported [writable_mode]: {mode}")

    c.info("Make directories and files writable")
