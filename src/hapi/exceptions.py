class ConfigurationError(Exception):
    pass


class ContextError(RuntimeError):
    pass


class GracefulShutdown(RuntimeError):
    pass


class InvalidProviderClass(ValueError):
    pass


class InvalidRemotesDefinition(ValueError):
    pass


class InvalidHookKind(ValueError):
    pass


class ItemNotFound(Exception):
    pass


class TaskNotFound(ItemNotFound):
    @staticmethod
    def with_name(name: str):
        return TaskNotFound(f'Task "{name}" was not found.')


class RemoteNotFound(ItemNotFound):
    pass
