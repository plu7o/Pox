from abc import ABC, abstractmethod
from Lexer.token import Token


class Expr(ABC):
    class Visitor(ABC):
        @abstractmethod
        def visit_assign_expr(self, expr):
            pass

        @abstractmethod
        def visit_binary_expr(self, expr):
            pass

        # @abstractmethod
        # def visit_call_expr(self, expr):
        #    pass

        # @abstractmethod
        # def visit_get_expr(self, expr):
        #    pass

        @abstractmethod
        def visit_grouping_expr(self, expr):
            pass

        @abstractmethod
        def visit_literal_expr(self, expr):
            pass

        @abstractmethod
        def visit_logical_expr(self, expr):
            pass

        # @abstractmethod
        # def visit_set_expr(self, expr):
        #    pass

        # @abstractmethod
        # def visit_super_expr(self, expr):
        #    pass

        # @abstractmethod
        # def visit_this_expr(self, expr):
        #    pass

        @abstractmethod
        def visit_unary_expr(self, expr):
            pass

        @abstractmethod
        def visit_variable_expr(self, expr):
            pass

    # Nested _expr classes here...

    @abstractmethod
    def accept(self, visitor: Visitor):
        pass

    class Assign:
        def __init__(self, name: Token, value):
            self.name = name
            self.value = value

        def accept(self, visitor):
            return visitor.visit_assign_expr(self)

    class Variable:
        def __init__(self, name: Token):
            self.name = name

        def accept(self, visitor):
            return visitor.visit_variable_expr(self)

    class Binary:
        def __init__(self, left, operator: Token, right):
            self.left = left
            self.operator = operator
            self.right = right

        def accept(self, visitor):
            return visitor.visit_binary_expr(self)

    class Grouping:
        def __init__(self, expression):
            self.expression = expression

        def accept(self, visitor):
            return visitor.visit_grouping_expr(self)

    class Literal:
        def __init__(self, value: object):
            self.value = value

        def accept(self, visitor):
            return visitor.visit_literal_expr(self)

        def __repr__(self) -> str:
            return f"Literal value: {self.value}"

    class Unary:
        def __init__(self, operator: Token, right):
            self.operator = operator
            self.right = right

        def accept(self, visitor):
            return visitor.visit_unary_expr(self)

    class Logical:
        def __init__(self, left, operator, right) -> None:
            self.left = left
            self.operator = operator
            self.right = right

        def accept(self, visitor):
            return visitor.visit_logical_expr(self)
