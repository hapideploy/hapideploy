class Logger:
    def __init__(self):
        pass

    def info(self, message: str, context: dict = None):
        self.write(level="INFO", message=message, context=context)

    def debug(self, message: str, context: dict = None):
        self.write(level="DEBUG", message=message, context=context)

    def write(self, level: str, message: str, context: dict = None):
        pass
