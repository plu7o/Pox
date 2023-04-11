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

    def visit_expression_stmt(self, stmt: Stmt.Expression):
        self.resolve_expr(stmt.expression)
        return None

    def visit_function_stmt(self, stmt: Stmt.Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt)
        return None

    def visit_if_stmt(self, stmt: Stmt.If):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        if stmt.else_branch != None:
            self.resolve_stmt(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt: Stmt.Print):
        if stmt.value != None:
            self.resolve_expr(stmt.value)
        return None

    def visit_var_stmt(self, stmt: Stmt.Var):
        self.declare(stmt.name)
        if stmt.initializer != None:
            self.resolve_stmt(stmt.initializer)

        self.define(stmt.name)
        return None
    
    def visit_while_stmt(self, stmt: Stmt.While):
        self.resolve_expr(stmt.condition)
        self.resolve(stmt.body)
        return None

    def visit_assign_expr(self, expr: Expr.Assign):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)
        return None

    def visit_binary_expr(self, expr: Expr.Binary):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
        return None

    def vitis_call_expr(self, expr: Expr.Call):
        self.resolve_expr(expr.callee)

        for arg in expr.arguments:
            self.resolve_expr(arg)

        return None

    def visit_group_expr(self, expr: Expr.Grouping):
        self.resolve_expr(expr.expression)
        return None

    def visit_literal_expr(self, expr: Expr.Literal):
        return None

    def visit_logical_expr(self, expr: Expr.Logical):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
        return None

    def visit_unary_expr(self, expr: Expr.Unary):
        self.resolve_expr(expr.right)
        return None

    def visit_variable_expr(self, expr: Expr.Variable):
        if len(self.scopes) == 0 and self.scopes[0][expr.name.lexeme] == False:
            import pox as Pox

            Pox.pox.parse_error(
                expr.name, "Can't read local Variable in its own initializer."
            )

        self.resolve_local(expr, expr.name)
        return None

    def resolve_stmt(self, stmt: Stmt):
        stmt.accept(self)

    def resolve_expr(self, expr: Expr):
        expr.accept(self)
