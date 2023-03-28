from Eval.expressions import Expr
from Eval.statements import Stmt
from Lexer.token_type import TokenType
from Lexer.token import Token
from Errors.runtime_error import Runtime_error
from Env.environment import Environment


class Interpreter(Expr.Visitor, Stmt.Visitor):
    def __init__(self) -> None:
        self.env = Environment()

    def interpret(self, statements: list[Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except Runtime_error as error:
            from pox import Pox

            Pox.runtime_error(error)

    def visit_assign_expr(self, expr):
        raise NotImplemented

    def visit_literal_expr(self, expr: Expr.Literal) -> object:
        return expr.value

    def visit_grouping_expr(self, expr: Expr.Grouping) -> object:
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: Expr.Unary) -> object:
        right = self.evaluate(expr.right)

        if expr.operator.token_type == TokenType.MINUS:
            return -float(right)
        elif TokenType.BANG:
            return not self.is_truthy(right)

        # unreachable
        return None

    def visit_variable_expr(self, expr: Expr.Variable):
        return self.env.get(expr.name)

    def check_number_operand(self, operator: Token, operand: object) -> None:
        if isinstance(operand, float):
            return
        raise Runtime_error(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: object, right: object):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise Runtime_error(operator, "Operand must be a number.")

    def is_truthy(self, obj: object) -> bool:
        if obj == None:
            return False

        if isinstance(obj, bool):
            return True

        return True

    def is_equal(self, a: object, b: object) -> bool:
        if a == None and b == None:
            return True
        if a == None:
            return False

        return a == b

    def stringify(self, obj: object) -> str:
        if obj == None:
            return "Nil"

        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[: len(text) - 2]

            return text

        return str(obj)

    def evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def visit_expression_stmt(self, stmt: Stmt.Expression):
        self.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt: Stmt.Print):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_var_stmt(self, stmt: Stmt.Var):
        value = None
        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)

        self.env.define(stmt.name.lexeme, value)
        return None

    def visit_binary_expr(self, expr: Expr.Binary) -> object:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) or isinstance(right, str):
                    return str(self.stringify(left)) + str(self.stringify(right))
                raise Runtime_error(
                    expr.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                if left == 0 or right == 0:
                    raise Runtime_error(
                        expr.operator, f"Trying to devide by Zero: {left} / {right}"
                    )
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)

        # unreachable
        return None
