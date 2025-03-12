class BindingException(Exception):
    @staticmethod
    def with_key(key: str):
        return BindingException(f'The key "{key}" is not defined in the container.')
