from .token import Token
class RuntimeError_(RuntimeError):
    '''Custom RuntimeError for interpreter'''
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(message)

