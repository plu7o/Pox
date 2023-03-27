from Eval.expressions import Expr


class AstPrinter(Expr.Visitor):
    def print_ast(self, expr: Expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Expr.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.left, expr.right])

    def visit_grouping_expr(self, expr: Expr.Grouping) -> str:
        return self.parenthesize("group", [expr.expression])

    def visit_literal_expr(self, expr: Expr.Literal):
        if expr.value == None:
            return "Nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Expr.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.right])

    def parenthesize(self, name: str, exprs: list[Expr]) -> str:
        global length
        string = f'( {name}'
        space = ' '
        for i, expr in enumerate(exprs):
            string += f' {expr.accept(self)}'
        string += ' )'

        return str(string)
