from ...core.program import Provider
from .check import provision_check


class Provision(Provider):
    @staticmethod
    def tasks():
        return [
            ("provision:check", "Checks pre-required state", provision_check),
        ]
