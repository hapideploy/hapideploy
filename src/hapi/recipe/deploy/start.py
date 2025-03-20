from ...core import Context


def deploy_start(c: Context):
    release_name = (
        int(c.cat("{{deploy_path}}/.dep/latest_release")) + 1
        if c.test("[ -f {{deploy_path}}/.dep/latest_release ]")
        else 1
    )

    c.put("release_name", release_name)

    c.info("Deploying {{name}} to {{stage}} (release: {{release_name}})")
