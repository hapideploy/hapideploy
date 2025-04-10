class ConfigurationError(RuntimeError):
    pass


class ContextError(Exception):
    pass


class GracefulShutdown(Exception):
    pass


class InvalidProviderClass(TypeError):
    pass


class InvalidHostsDefinition(ValueError):
    pass


class InvalidHookKind(ValueError):
    pass


class ItemNotFound(ValueError):
    pass


class TaskNotFound(ItemNotFound):
    @staticmethod
    def with_name(name: str):
        return TaskNotFound(f'Task "{name}" is not found.')


class RemoteNotFound(ItemNotFound):
    pass
