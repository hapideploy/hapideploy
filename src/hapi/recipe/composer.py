from ..core import Context


def composer_install(c: Context):
    c.run("cd {{release_path}} && composer install")
