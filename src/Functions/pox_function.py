from .pox_callable import PoxCallable
from Eval.statements import Stmt
from Env.environment import Environment
from .pox_return import PoxReturn

class PoxFunction(PoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment) -> None:
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments: list) -> object:
        env = Environment(interpreter.global_env)

        for i in range(len(self.declaration.params)):
            env.define(self.declaration.params[i].lexeme, arguments[i])
        
        try:
            interpreter.execute_block(self.declaration.body, env)
        except PoxReturn as return_value:
            return return_value.value

        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def __repr__(self) -> str:
        return f'"<Fn {self.declaration.name.lexeme}>"'

