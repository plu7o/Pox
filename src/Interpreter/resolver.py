from Eval.expressions import Expr
from Eval.statements import Stmt


class Resolver(Expr.Visitor, Stmt.Visitor):
    def __init__(self, interpteter) -> None:
        self.interpteter = interpteter
        self.scopes = []

    def resolve(self, statements: list[Stmt]):
        for stmt in statements:
            self.resolve_stmt(stmt)

    def resolve_function(self, func: Stmt.Function):
        self.begin_scope()

        for param in func.params:
            self.declare(param)
            self.define(param)

        self.resolve(func.body)
        self.end_scope()

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop(-1)

    def declare(self, name):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[0]
        scope[name.lexeme] = False

    def define(self, name):
        if len(self.scopes) == 0:
            self.scopes[0][name.lexeme] = True

    def resolve_local(expr: Expr, name):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpteter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def visit_block_stmt(self, stmt: Stmt.block):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None

    def visit_function_stmt(self, stmt: Stmt.Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt)
        return None

    def visit_var_stmt(self, stmt: Stmt.Var):
        self.declare(stmt.name)
        if stmt.initializer != None:
            self.resolve_stmt(stmt.initializer)

        self.define(stmt.name)
        return None

    def visit_assign_expr(self, expr: Expr.Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
        return None

    def visit_variable_expr(self, expr: Expr.Variable):
        if len(self.scopes) == 0 and self.scopes[0][expr.name.lexeme] == False:
            import pox as pox

            Pox.pox.parse_error(
                expr.name, "Can't read local Variable in its own initializer."
            )

        self.resolve_local(expr, expr.name)
        return None

    def resolve_stmt(self, stmt: Stmt):
        stmt.accept(self)

    def resolve_expr(self, expr: Expr):
        expr.accept(self)
