from Errors.runtime_error import Runtime_error
from Lexer.token import Token

class Environment:
    def __init__(self) -> None:
        self.values = {}

    def get(self, name: Token) -> object:
        if self.values.get(name.lexeme) is not None:
            return self.values[name.lexeme]

        raise Runtime_error(name, f'Undefined variable "{name.lexeme}".')


    def define(self, name: str, value: object):
        self.values[name] = value



