class Logger:
    LEVEL_DEBUG = "DEBUG"

    def debug(self, message: str, context: dict = None):
        self.write(level=Logger.LEVEL_DEBUG, message=message, context=context)

    def write(self, level: str, message: str, context: dict = None):
        raise NotImplemented
