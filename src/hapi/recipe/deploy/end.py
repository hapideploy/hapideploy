from ...core import Context


def deploy_end(c: Context):
    deployed = c.cook("deployed")
    if deployed:
        c.info("Deployed {{name}} to stage={{stage}} (release: {{deployed}})")
    else:
        c.info("There is not a deployed release of {{name}} on stage={{stage}}.")
