from ...core import Deployer
from ..binding import bin_symlink as resolve_bin_symlink
from ..binding import release_path as resolve_release_path


def deploy_shared(dep: Deployer):
    shared_dir_items = dep.make("shared_dirs", [])

    for a in shared_dir_items:
        for b in shared_dir_items:

            if a != b and (a.rstrip("/") + "/").find(b.rstrip("/") + "/") == 0:
                raise Exception(f"Can not share same directories {a} and {b}")

    shared_path = "{{deploy_path}}/shared"
    bin_symlink = resolve_bin_symlink(dep)
    release_path = resolve_release_path(dep)

    copy_verbosity = "v" if dep.io().debug() else ""

    # Share directories
    for item_dir in shared_dir_items:
        item_dir = item_dir.strip("/")

        if not dep.test(f"[ -d {shared_path}/{item_dir} ]"):
            dep.run(f"mkdir -p {shared_path}/{item_dir}")

            if dep.test(f"[ -d $(echo {release_path}/{item_dir}) ]"):
                segments = item_dir.split("/")
                segments.pop()
                dirname = "/".join(segments)
                dep.run(
                    f" cp -r{copy_verbosity} {release_path}/{item_dir} {shared_path}/{dirname}"
                )

        dep.run(f"rm -rf {release_path}/{item_dir}")

        dep.run(f"mkdir -p `dirname {release_path}/{item_dir}`")

        dep.run(f"{bin_symlink} {shared_path}/{item_dir} {release_path}/{item_dir}")

    shared_file_items = dep.make("shared_files", [])

    # Share files
    for item_file in shared_file_items:
        segments = dep.parse(item_file).split("/")
        segments.pop()
        dirname = "/".join(segments)

        if not dep.test("[ -d %s/%s ]" % (shared_path, dirname)):
            dep.run(
                f"cp -r{copy_verbosity} {release_path}/{item_file} {shared_path}/{item_file}"
            )

        dep.run(
            f"if [ -f $(echo {release_path}/{item_file}) ]; then rm -rf {release_path}/{item_file}; fi"
        )

        dep.run(
            f"if [ ! -d $(echo {release_path}/{dirname}) ]; then mkdir -p {release_path}/{dirname};fi"
        )

        dep.run(f"[ -f {shared_path}/{item_file} ] || touch {shared_path}/{item_file}")

        dep.run(f"{bin_symlink} {shared_path}/{item_file} {release_path}/{item_file}")

    dep.info("Shared directories and files.")
