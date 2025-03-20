from ...core import Context


def deploy_shared(c: Context):
    shared_dirs = c.cook("shared_dirs", [])

    for a in shared_dirs:
        for b in shared_dirs:

            if a != b and (a.rstrip("/") + "/").find(b.rstrip("/") + "/") == 0:
                raise Exception(f"Can not share same directories {a} and {b}")

    shared_path = "{{deploy_path}}/shared"

    bin_symlink = c.cook("bin/symlink")
    release_path = c.cook("release_path")

    copy_verbosity = "v" if c.io().debug() else ""

    # Share directories
    for item_dir in shared_dirs:
        item_dir = item_dir.strip("/")

        if not c.test(f"[ -d {shared_path}/{item_dir} ]"):
            c.run(f"mkdir -p {shared_path}/{item_dir}")

            if c.test(f"[ -d $(echo {release_path}/{item_dir}) ]"):
                segments = item_dir.split("/")
                segments.pop()
                dirname = "/".join(segments)
                c.run(
                    f" cp -r{copy_verbosity} {release_path}/{item_dir} {shared_path}/{dirname}"
                )

        c.run(f"rm -rf {release_path}/{item_dir}")

        c.run(f"mkdir -p `dirname {release_path}/{item_dir}`")

        c.run(f"{bin_symlink} {shared_path}/{item_dir} {release_path}/{item_dir}")

    shared_files = c.cook("shared_files", [])

    # Share files
    for item_file in shared_files:
        segments = c.parse(item_file).split("/")
        segments.pop()
        dirname = "/".join(segments)

        if not c.test("[ -d %s/%s ]" % (shared_path, dirname)):
            c.run(
                f"cp -r{copy_verbosity} {release_path}/{item_file} {shared_path}/{item_file}"
            )

        c.run(
            f"if [ -f $(echo {release_path}/{item_file}) ]; then rm -rf {release_path}/{item_file}; fi"
        )

        c.run(
            f"if [ ! -d $(echo {release_path}/{dirname}) ]; then mkdir -p {release_path}/{dirname};fi"
        )

        c.run(f"[ -f {shared_path}/{item_file} ] || touch {shared_path}/{item_file}")

        c.run(f"{bin_symlink} {shared_path}/{item_file} {release_path}/{item_file}")

    c.info("Shared directories and files.")
