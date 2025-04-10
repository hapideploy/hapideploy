from ..core import Provider
from ..utils import (
    bin_git,
    bin_symlink,
    release_path,
    releases_list,
    releases_log,
    target,
)
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
            ("deploy:start", "Start a new deployment", deploy_start),
            ("deploy:setup", "Setup the deploy directory", deploy_setup),
            ("deploy:release", "Create a new release", deploy_release),
            ("deploy:code", "Update code", deploy_code),
            ("deploy:env", "Create the .env file", deploy_env),
            ("deploy:shared", "Share directories and files", deploy_shared),
            ("deploy:lock", "Lock the deployment", deploy_lock),
            ("deploy:unlock", "Unlock the deployment", deploy_unlock),
            ("deploy:writable", "Make directories and files writable", deploy_writable),
            ("deploy:main", "Deploy main activities", lambda _: None),
            ("deploy:symlink", "Create the release symlink", deploy_symlink),
            ("deploy:clean", "Clean deployment stuff", deploy_clean),
            ("deploy:success", "Announce a deployment is suceed", deploy_success),
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
                "deploy:success",
            ],
        )

        self.app.define_group(
            "deploy:failed",
            "Do something if deploy task is failed",
            ["deploy:unlock"],
        )

        self.app.fail("deploy", "deploy:failed")
