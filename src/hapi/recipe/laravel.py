from .npm import bin_npm, npm_build, npm_install
from .php import PHP


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

        self.app.register_task("npm:install", "Install NPM packages", npm_install)
        self.app.register_task("npm:build", "Execute NPM build script", npm_build)

        self.app.register_hook(
            "after",
            "composer:install",
            [
                "npm:install",
                "npm:build",
            ],
        )
