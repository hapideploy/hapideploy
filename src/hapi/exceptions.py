class GracefulShutdown(Exception):
    pass


class StoppedException(Exception):
    pass


class KeyNotFound(ValueError):
    pass


class InvalidProviderClass(TypeError):
    pass


class InvalidHostsDefinition(ValueError):
    pass


class ItemNotFound(ValueError):
    pass


class CommandNotFound(ItemNotFound):
    @staticmethod
    def with_name(name: str):
        return CommandNotFound(f"Command {name} is not found.")


class TaskNotFound(ItemNotFound):
    @staticmethod
    def with_name(name: str):
        return TaskNotFound(f"Task {name} is not found.")


class RemoteNotFound(ItemNotFound):
    pass


class CurrentRemoteNotSet(ValueError):
    pass


class CurrentTaskNotSet(ValueError):
    pass


class InvalidHookKind(ValueError):
    pass
