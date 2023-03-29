from Lexer.token import Token

class Runtime_error(RuntimeError):
    def __init__(self, token: Token = None, message: str = None) -> None:
        self.message = message
        self.token = token
