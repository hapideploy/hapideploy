from ..core import Provider
from ..utils import (
    bin_composer,
    bin_php,
    composer_install,
    fpm_reload,
    fpm_restart,
)
from .common import Common


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

        self.app.after("deploy:symlink", "fpm:restart")
