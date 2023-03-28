from Errors.runtime_error import Runtime_error
from Lexer.token import Token


class Environment:
    def __init__(self, enclosing=None) -> None:
        self.enclosing = enclosing
        self.values = {}

    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise Runtime_error(name, f'Undefined variable "{name.lexeme}".')

    def assign(self, name: Token, value: object) -> object:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise Runtime_error(name, f'Undefined variable "{name.lexeme}".')

    def define(self, name: str, value: object):
        self.values[name] = value
