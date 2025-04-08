from ..core import Context
from .common import Common


def bin_php(c: Context):
    version = c.cook("php_version") if c.check("php_version") else ""

    return c.which(f"php{version}")


def bin_composer(c: Context):
    return c.cook("bin/php") + " " + c.which("composer")


def composer_install(c: Context):
    release_path = c.cook("release_path")
    composer = c.cook("bin/composer")
    options = c.cook(
        "composer_install_options",
        "--no-ansi --verbose --prefer-dist --no-progress --no-interaction --no-dev --optimize-autoloader",
    )

    c.run(f"cd {release_path} && {composer} install {options}")


def fpm_reload(c: Context):
    c.run("sudo systemctl reload php{{php_version}}-fpm")


def fpm_restart(c: Context):
    c.run("sudo systemctl restart php{{php_version}}-fpm")


class PHP(Common):
    def register(self):
        super().register()

        self.app.bind("bin/php", bin_php)
        self.app.bind("bin/composer", bin_composer)

        items = [
            ("composer:install", "Install Composer dependencies", composer_install),
            ("fpm:reload", "Reload PHP-FPM", fpm_reload),
            ("fpm:restart", "Restart PHP-FPM", fpm_restart),
        ]

        for item in items:
            name, desc, func = item
            self.app.define_task(name, desc, func)

        self.app.define_hook("after", "deploy:writable", "composer:install")
        self.app.define_hook("after", "deploy:symlink", "fpm:restart")
