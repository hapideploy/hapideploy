from ..core import Context
from .npm import bin_npm, npm_build, npm_install
from .php import PHP


def artisan(command: str):
    def caller(c: Context):
        bin_php = c.cook("bin/php")
        artisan_file = "{{release_path}}/artisan"
        c.run(f"{bin_php} {artisan_file} {command}")

    return caller


class Laravel(PHP):
    def register(self):
        super().register()

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

        self.app.define_task(
            "artisan:storage:link",
            "Create the symbolic links",
            artisan("storage:link --force"),
        )
        self.app.define_task(
            "artisan:optimize",
            "Optimize application configuration",
            artisan("optimize"),
        )
        self.app.define_task(
            "artisan:migrate", "Run database migrations", artisan("migrate --force")
        )
        self.app.define_task(
            "artisan:db:seed", "Seed the database", artisan("db:seed --force")
        )

        self.app.define_task("npm:install", "Install NPM packages", npm_install)
        self.app.define_task("npm:build", "Execute NPM build script", npm_build)

        self.app.define_hook(
            "after",
            "composer:install",
            [
                "npm:install",
                "artisan:optimize",
                "artisan:storage:link",
                "artisan:migrate",
                # "artisan:db:seed",
                "npm:build",
            ],
        )
