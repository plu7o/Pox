from .pox_callable import PoxCallable
from Eval.statements import Stmt
from Env.environment import Environment

class PoxFunction(PoxCallable):
    def __init__(self, declaration: Stmt.Function) -> None:
        self.declaration = declaration

    def call(self, interpreter, arguments: list) -> object:
        env = Environment(interpreter.global_env)

        for i in range(len(self.declaration.params)):
            env.define(self.declaration.params[i].lexeme, arguments[i])

        interpreter.execute_block(self.declaration.body, env)
        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def __repr__(self) -> str:
        return f'"<Fn {self.declaration.name.lexeme}>"'

