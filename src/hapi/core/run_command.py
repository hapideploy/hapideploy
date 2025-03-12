from fabric import Connection

from .remote import Remote
from .run_result import RunResult


# @internal
class RunCommand:
    def __init__(self, remote: Remote, command: str):
        self.remote = remote
        self.command = command
        self.res = None

    def run(self):
        # If it already run, do not run again.
        if self.res:
            return

        # Open a connection
        conn = Connection(
            host=self.remote.host, user=self.remote.user, port=self.remote.port
        )

        # TODO: try/except. Check the run result, raise an informative exception when needed.
        origin = conn.run(self.command, hide=True)

        self.res = RunResult(origin)

        return self.res
