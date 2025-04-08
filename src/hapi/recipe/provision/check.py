from configparser import ConfigParser

from packaging.version import Version

from hapi import Context


def provision_check(c: Context):
    c.remote.user = c.cook("provision_user", "root")

    release = c.cat("/etc/os-release")

    parser = ConfigParser()

    parser.read_string(f"[DEFAULT]\n{release}")

    name = parser.get("DEFAULT", "NAME").strip('"')
    version_id = parser.get("DEFAULT", "VERSION_ID").strip('"')

    if name != "Ubuntu":
        raise RuntimeError("Only Ubuntu is supported.")

    if Version(version_id) > Version("24.04"):
        raise RuntimeError("Only Ubuntu 22.04 and 24.04 is supported.")
