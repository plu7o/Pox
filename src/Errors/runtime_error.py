from Lexer.token import Token

class Runtime_error(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__()
        self.message = message
        self.token = token
