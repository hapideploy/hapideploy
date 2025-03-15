from hapi.recipe.common import CommonProvider


class Laravel(CommonProvider):
    def register(self):
        super().register()

        self.app.put("shared_dirs", ["storage"])
        self.app.put("shared_files", [".env"])
