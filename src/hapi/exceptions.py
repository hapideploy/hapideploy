class RuntimeException(Exception):
    pass


class StoppedException(Exception):
    pass


class KeyNotFound(RuntimeException):
    pass


class InvalidProviderClass(TypeError):
    pass


class InvalidHostsDefinition(Exception):
    pass


class ItemNotFound(Exception):
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
    # @staticmethod
    # def with_name(name: str):
    #     return TaskNotFound(f'Remote {key} is not found.')


class ParsingRecurredKey(Exception):
    @staticmethod
    def with_key(key: str):
        return ParsingRecurredKey(f"The key [{key}] is a recurred key when parsing.")


class CurrentRemoteNotSet(RuntimeException):
    pass


class CurrentTaskNotSet(RuntimeException):
    pass


class InvalidHookKind(RuntimeException):
    pass
