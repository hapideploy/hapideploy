from invoke import UnexpectedExit

from ..core import Context


def bin_npm(c: Context):
    if not c.test("[ -d $HOME/.nvm ]"):
        c.raise_error(
            "nvm might not installed. Please install nvm to use node and npm."
        )

    if not c.test("[ -d $HOME/.nvm/versions/node/v{{node_version}} ]"):
        c.raise_error(
            "node version {{node_version}} does not exist. Try run 'nvm install {{node_version}}'."
        )

    return 'export PATH="$HOME/.nvm/versions/node/v{{node_version}}/bin:$PATH"; npm'


def bin_pm2(c: Context):
    if not c.test("[ -d $HOME/.nvm ]"):
        c.raise_error(
            "nvm might not installed. Please install nvm to use node and npm."
        )

    if not c.test("[ -d $HOME/.nvm/versions/node/v{{node_version}} ]"):
        c.raise_error(
            "node version {{node_version}} does not exist. Try to run 'nvm install {{node_version}}'."
        )

    return 'export PATH="$HOME/.nvm/versions/node/v{{node_version}}/bin:$PATH"; pm2'


def npm_install(c: Context):
    c.run("cd {{release_path}} && {{bin/npm}} install")


def npm_ci(c: Context):
    c.run("cd {{release_path}} && {{bin/npm}} ci")


def npm_build(c: Context):
    c.run("cd {{release_path}} && {{bin/npm}} run {{npm_build_script}}")


def pm2_process_name(c: Context):
    return c.parse("{{name}}-{{stage}}")


def pm2_stop(c: Context):
    c.run("{{bin/pm2}} stop {{pm2_process_name}} >> /dev/null")


def pm2_del(c: Context):
    c.run("{{bin/pm2}} del {{pm2_process_name}} >> /dev/null")


def pm2_start(c: Context):
    c.run(
        "{{bin/pm2}} start {{pm2_start_script_path}} --name={{pm2_process_name}} >> /dev/null"
    )
