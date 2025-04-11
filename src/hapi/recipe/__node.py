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
            "node version {{node_version}} does not exist. Try run 'nvm install {{node_version}}'."
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


def pm2_start(c: Context):
    process_name = c.cook("pm2_process_name")
    try:
        c.run("{{bin/pm2}} stop {{pm2_process_name}}").fetch()
        c.run("{{bin/pm2}} del {{pm2_process_name}}")
    except UnexpectedExit as e:
        if (
            str(e).find(f"[PM2][ERROR] Process or Namespace {process_name} not found")
            == -1
        ):
            raise e

    c.run("{{bin/pm2}} start {{release_path}}/bin/www --name={{pm2_process_name}}")


def pm2_status(c: Context):
    command = c.parse("{{bin/pm2}} status")
    c.remote.connect().run(command)
    pass
    # TODO UnicodeEncodeError: 'charmap' codec can't encode character '\ufffd' in position 441: character maps to <undefined>
    # c.run("{{bin/pm2}} status {{pm2_process_name}}")
