from hapi.recipe.common import CommonProvider


class Laravel(CommonProvider):
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
