from Eval.expressions import Expr
from Eval.statements import Stmt
from Lexer.token_type import TokenType
from Lexer.token import Token
from Errors.runtime_error import Runtime_error
from Env.environment import Environment
from Functions.pox_callable import PoxCallable
from Functions.pox_function import PoxFunction
import time


class Interpreter(Expr.Visitor, Stmt.Visitor):
    def __init__(self) -> None:
        self.global_env = Environment()
        self.env = self.global_env
        self.global_env.define(
            "clock",
            type(
                "Clock",
                (PoxCallable,),
                {
                    "arity": lambda self: 0,
                    "calll": lambda self, interpreter, arguments: time.time(),
                    "__repr__": lambda self: "<native fn>",
                },
            ),
        )

    def interpret(self, statements: list[Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except Runtime_error as error:
            import pox as Pox

            Pox.pox.runtime_error(error)

    def visit_literal_expr(self, expr: Expr.Literal) -> object:
        return expr.value

    def visit_logical_expr(self, expr: Expr.Logical) -> object:
        left = self.evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

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
        value = self.env.get(expr.name)
        if value == None:
            raise Runtime_error(
                expr.name, f'Can\'t access uninitialized variable "{expr.name.lexeme}".'
            )
        return value

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
            return obj

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

    def execute_block(self, statements: list[Stmt], env: Environment):
        previous = self.env
        try:
            self.env = env

            for statement in statements:
                self.execute(statement)

        finally:
            self.env = previous

    def visit_block_stmt(self, stmt: Stmt.Block):
        self.execute_block(stmt.statements, Environment(self.env))
        return None

    def visit_expression_stmt(self, stmt: Stmt.Expression):
        self.evaluate(stmt.expression)
        return None

    def visit_function_stmt(self, stmt: Stmt.Function):
        function = PoxFunction(stmt)
        self.env.define(stmt.name.lexeme, function)
        return None

    def visit_if_stmt(self, stmt: Stmt.If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)

        elif stmt.else_branch != None:
            self.execute(stmt.else_branch)

        return None

    def visit_print_stmt(self, stmt: Stmt.Print):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_var_stmt(self, stmt: Stmt.Var):
        value = None
        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)

        self.env.define(stmt.name.lexeme, value)
        return None

    def visit_while_stmt(self, stmt: Stmt.While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def visit_assign_expr(self, expr: Expr.Assign) -> object:
        value = self.evaluate(expr.value)
        self.env.assign(expr.name, value)
        return value

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

    def visit_call_expr(self, expr: Expr.Call) -> object:
        callee = self.evaluate(expr.callee)

        args = []
        for arg in expr.arguments:
            args.append(self.evaluate(arg))

        if not isinstance(callee, PoxCallable):
            raise Runtime_error(expr.paren, "Can only call function and classes.")

        function = callee

        if len(args) != function.arity():
            raise Runtime_error(
                expr.paren,
                f"Expected {function.arity()} arguments but got {len(args)}.",
            )

        return function.call(self, args)
