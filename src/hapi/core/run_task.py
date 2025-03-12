from .remote import Remote
from .task import Task


# @internal
class RunTask:
    def __init__(self, remote: Remote, task: Task):
        self.remote = remote
        self.task = task
