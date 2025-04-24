from typing import Any

from ..core import Context, Provider
from .deploy import (
    deploy_clean,
    deploy_code,
    deploy_end,
    deploy_env,
    deploy_lock,
    deploy_release,
    deploy_setup,
    deploy_shared,
    deploy_start,
    deploy_symlink,
    deploy_unlock,
    deploy_writable,
)


def bin_git(c: Context):
    return c.which("git")


def bin_symlink(c: Context):
    return "ln -nfs --relative" if c.cook("use_relative_symlink") is True else "ln -nfs"


def target(c: Context):
    if c.check("branch"):
        return c.cook("branch")

    if c.check("tag"):
        return c.cook("tag")

    if c.check("revision"):
        return c.cook("revision")

    return "HEAD"


def release_path(c: Context):
    if c.test("[ -h {{deploy_path}}/release ]"):
        link = c.run("readlink {{deploy_path}}/release").fetch()
        return link if link[0] == "/" else c.parse("{{deploy_path}}" + "/" + link)

    c.raise_error('The "release_path" ({{deploy_path}}/release) does not exist.')


def releases_log(c: Context):
    import json

    if c.test("[ -f {{deploy_path}}/.dep/releases_log ]") is False:
        return []

    lines = c.run("tail -n 300 {{deploy_path}}/.dep/releases_log").fetch().split("\n")
    releases: list[Any] = []
    for line in lines:
        releases.insert(0, json.loads(line))
    return releases


def releases_list(c: Context):
    if (
        c.test(
            '[ -d {{deploy_path}}/releases ] && [ "$(ls -A {{deploy_path}}/releases)" ]'
        )
        is False
    ):
        return []

    ll = c.run("cd {{deploy_path}}/releases && ls -t -1 -d */").fetch().split("\n")
    ll = list(map(lambda x: x.strip("/"), ll))

    release_items = c.cook("releases_log")

    releases = []

    for candidate in release_items:
        if str(candidate["release_name"]) in ll:
            releases.append(str(candidate["release_name"]))

    return releases


class Common(Provider):
    def register(self):
        self._register_put()

        self._register_bind()

        self._register_tasks()

        self._register_deploy_task()

    def _register_put(self):
        self.app.put("dotenv_example", ".env.example")
        self.app.put("current_path", "{{deploy_path}}/current")
        self.app.put("update_code_strategy", "archive")
        self.app.put("git_ssh_command", "ssh -o StrictHostKeyChecking=accept-new")
        self.app.put("sub_directory", False)
        self.app.put("shared_dirs", [])
        self.app.put("shared_files", [])
        self.app.put("writable_dirs", [])
        self.app.put("writable_mode", "group")
        self.app.put("writable_recursive", True)
        self.app.put("writable_use_sudo", False)
        self.app.put("writable_user", "www-data")
        self.app.put("writable_group", "www-data")

    def _register_bind(self):
        self.app.bind("bin/git", bin_git)
        self.app.bind("bin/symlink", bin_symlink)

        self.app.bind("target", target)
        self.app.bind("release_path", release_path)
        self.app.bind("releases_log", releases_log)
        self.app.bind("releases_list", releases_list)

    def _register_tasks(self):
        for name, desc, func in [
            ("deploy:start", "Start a deployment", deploy_start),
            ("deploy:setup", "Setup the deploy path", deploy_setup),
            ("deploy:release", "Create a new release", deploy_release),
            ("deploy:code", "Update the code", deploy_code),
            ("deploy:env", "Create the .env file", deploy_env),
            ("deploy:shared", "Share directories and files", deploy_shared),
            ("deploy:lock", "Lock the deployment process", deploy_lock),
            ("deploy:unlock", "Unlock the deployment process", deploy_unlock),
            ("deploy:writable", "Make directories and files writable", deploy_writable),
            ("deploy:main", "Deploy main activities", lambda _: None),
            ("deploy:symlink", "Symlink the current path", deploy_symlink),
            ("deploy:clean", "Clean deployment stuff", deploy_clean),
            ("deploy:end", "End a deployment", deploy_end),
        ]:
            self.app.define_task(name, desc, func)

    def _register_deploy_task(self):
        self.app.define_group(
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
                "deploy:main",
                "deploy:symlink",
                "deploy:unlock",
                "deploy:clean",
                "deploy:end",
            ],
        )

        self.app.define_group(
            "deploy:failed",
            "Do something if deploy task is failed",
            ["deploy:unlock"],
        )

        self.app.fail("deploy", "deploy:failed")
