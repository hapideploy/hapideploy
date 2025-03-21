from ..core import Context
from .common import CommonProvider


def bin_php(c: Context):
    version = c.cook("php_version") if c.check("php_version") else ""

    return c.which(f"php{version}")


def bin_composer(c: Context):
    return c.cook("bin/php") + " " + c.which("composer")


def composer_install(c: Context):
    options = c.cook(
        "composer_options",
        "--no-ansi --verbose --prefer-dist --no-progress --no-interaction --no-dev --optimize-autoloader",
    )

    c.run("cd {{release_path}} && {{bin/composer}} install " + options)


class PHP(CommonProvider):
    def register(self):
        super().register()

        self.app.bind("bin/php", bin_php)
        self.app.bind("bin/composer", bin_composer)

        items = [
            ("composer:install", "Install Composer dependencies", composer_install),
        ]

        for item in items:
            name, desc, func = item
            self.app.register_task(name, desc, func)

        self.app.register_hook("after", "deploy:writable", "composer:install")
