from ..core import Context


def bin_npm(c: Context):
    node_version = c.cook("node_version")

    return f'PATH="/home/vagrant/.nvm/versions/node/v{node_version}/bin:$PATH" npm'


def npm_install(c: Context):
    c.run("cd {{release_path}} && {{bin/npm}} {{npm_install_action}}")


def npm_build(c: Context):
    c.run("cd {{release_path}} && {{bin/npm}} run {{npm_build_script}}")
