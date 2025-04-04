from ..core import Provider
from .deploy import (
    deploy_clean,
    deploy_code,
    deploy_env,
    deploy_lock,
    deploy_release,
    deploy_setup,
    deploy_shared,
    deploy_start,
    deploy_success,
    deploy_symlink,
    deploy_unlock,
    deploy_writable,
)
from .functions import (
    bin_git,
    bin_symlink,
    release_path,
    releases_list,
    releases_log,
    target,
)


class Common(Provider):
    def register(self):
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

        self.app.bind("bin/git", bin_git)
        self.app.bind("bin/symlink", bin_symlink)
        self.app.bind("target", target)
        self.app.bind("release_path", release_path)
        self.app.bind("releases_log", releases_log)
        self.app.bind("releases_list", releases_list)

        items = [
            ("deploy:start", "Start a new deployment", deploy_start),
            ("deploy:setup", "Prepare the deployment directory", deploy_setup),
            ("deploy:release", "Prepare the release candidate", deploy_release),
            ("deploy:code", "Update code", deploy_code),
            ("deploy:env", "Configure .env file", deploy_env),
            (
                "deploy:shared",
                "Create symlinks for shared directories and files",
                deploy_shared,
            ),
            ("deploy:lock", "Lock the deployment process", deploy_lock),
            ("deploy:unlock", "Unlock the deployment process", deploy_unlock),
            ("deploy:writable", "Make directories and files writable", deploy_writable),
            ("deploy:symlink", "Creates the symlink to release", deploy_symlink),
            (
                "deploy:clean",
                "Clean deployment process, E.g. remove old release candidates",
                deploy_clean,
            ),
            (
                "deploy:success",
                "Announce the deployment process is suceed",
                deploy_success,
            ),
        ]

        for item in items:
            name, desc, func = item
            self.app.define_task(name, desc, func)

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
                # custom tasks
                "deploy:symlink",
                "deploy:unlock",
                "deploy:clean",
                "deploy:success",
            ],
        )

        self.app.define_group(
            "deploy:failed",
            "Activities should be done when deploy task is failed.",
            ["deploy:unlock"],
        )

        self.app.fail("deploy", "deploy:failed")
