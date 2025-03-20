from .common import CommonProvider
from .composer import composer_install


class PHP(CommonProvider):
    def register(self):
        super().register()

        items = [
            ("composer:install", "Install Composer dependencies", composer_install),
        ]

        for item in items:
            name, desc, func = item
            self.app.register_task(name, desc, func)

        self.app.register_hook("after", "deploy:writable", "composer:install")
