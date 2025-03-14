from .binding import BindingException
from .logic import LogicException
from .runtime import RuntimeException
from .stopped import StoppedException


class InvalidProviderClass(TypeError):
    pass


class InvalidHostsDefinition(Exception):
    pass
