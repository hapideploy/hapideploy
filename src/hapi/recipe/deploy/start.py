from ...core import Context


def deploy_start(c: Context):
    if c.test("[ -f {{deploy_path}}/.dep/latest_release ]"):
        latest_release = c.cat("{{deploy_path}}/.dep/latest_release")

        try:
            release_name = int(latest_release) + 1

            c.put("release_name", release_name)
        except ValueError:
            c.raise_error(
                f'Could not detect a release name because the latest release "{latest_release}" is not numeric. \nUse --put=release_name=* to set it.'
            )
    elif not c.check("release_name"):
        c.put("release_name", 1)

    c.info("Deploying {{name}} to stage={{stage}} (release: {{release_name}})")
