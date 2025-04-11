from ..core import Context, Provider
from .__node import bin_npm, npm_build, npm_install
from .common import Common
from .php import PHP


def artisan(command: str):
    def caller(c: Context):
        bin_php = c.cook("bin/php")
        artisan_file = "{{release_path}}/artisan"
        c.run(f"{bin_php} {artisan_file} {command}")

    return caller


class Laravel(Provider):
    def register(self):
        self.app.load(Common)
        self.app.load(PHP)

        self.app.put("shared_dirs", ["storage"])
        self.app.put("shared_files", [".env"])
        self.app.put(
            "writable_dirs",
            [
                "bootstrap/cache",
                "storage",
                "storage/app",
                "storage/app/public",
                "storage/framework",
                "storage/framework/cache",
                "storage/framework/cache/data",
                "storage/framework/sessions",
                "storage/framework/views",
                "storage/logs",
            ],
        )

        self.app.put("node_version", "20.19.0")
        self.app.put("npm_install_action", "install")  # install or ci
        self.app.put("npm_build_script", "build")

        self.app.bind("bin/npm", bin_npm)

        self._register_tasks()

        self.app.define_group(
            "deploy:main",
            "Deploy main activities",
            [
                "composer:install",
                "npm:install",
                "artisan:optimize",
                "artisan:storage:link",
                "artisan:migrate",
                # "artisan:db:seed",
                "npm:build",
            ],
        )

    def _register_tasks(self):
        for name, desc, func in [
            (
                "artisan:storage:link",
                "Create the storage symlink",
                artisan("storage:link --force"),
            ),
            ("artisan:optimize", "Increase performance", artisan("optimize")),
            ("artisan:migrate", "Run database migrations", artisan("migrate --force")),
            ("artisan:db:seed", "Seed the database", artisan("db:seed --force")),
            ("npm:install", "Install NPM packages", npm_install),
            ("npm:build", "Execute NPM build script", npm_build),
        ]:
            self.app.define_task(name, desc, func)
