from ..core import Context, Provider
from .common import Common


def bin_php(c: Context):
    version = c.cook("php_version") if c.check("php_version") else ""

    return c.which(f"php{version}")


def bin_composer(c: Context):
    return c.cook("bin/php") + " " + c.which("composer")


def composer_install(c: Context):
    composer = c.cook("bin/composer")
    options = c.cook(
        "composer_install_options",
        "--no-ansi --verbose --prefer-dist --no-progress --no-interaction --no-dev --optimize-autoloader",
    )

    c.run(f"cd {c.cook("release_path")} && {composer} install {options}")


def fpm_reload(c: Context):
    c.run("sudo systemctl reload php{{php_version}}-fpm")


def fpm_restart(c: Context):
    c.run("sudo systemctl restart php{{php_version}}-fpm")


class PHP(Provider):
    def register(self):
        self.app.load(Common)

        self.app.bind("bin/php", bin_php)
        self.app.bind("bin/composer", bin_composer)

        for name, desc, func in [
            ("composer:install", "Install Composer dependencies", composer_install),
            ("fpm:reload", "Reload PHP-FPM", fpm_reload),
            ("fpm:restart", "Restart PHP-FPM", fpm_restart),
        ]:
            self.app.define_task(name, desc, func)

        self.app.define_group(
            "deploy:main", "Deploy main activities", "composer:install"
        )
