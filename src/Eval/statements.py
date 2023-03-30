from abc import ABC, abstractmethod
from os import name


class Stmt(ABC):
    class Visitor(ABC):
        @abstractmethod
        def visit_block_stmt(self, stmt):
            pass

        # @abstractmethod
        # def visit_class_stmt(self, stmt):
        #    pass

        @abstractmethod
        def visit_expression_stmt(self, stmt):
            pass

        # @abstractmethod
        # def visit_function_stmt(self, stmt):
        #    pass

        @abstractmethod
        def visit_if_stmt(self, stmt):
            pass

        @abstractmethod
        def visit_print_stmt(self, stmt):
            pass

        # @abstractmethod
        # def visit_return_stmt(self, stmt):
        #    pass

        @abstractmethod
        def visit_var_stmt(self, stmt):
            pass

        @abstractmethod
        def visit_while_stmt(self, stmt):
            pass

    @abstractmethod
    def accept(self, visitor: Visitor):
        pass

    class Block:
        def __init__(self, statements: list):
            self.statements = statements

        def accept(self, visitor):
            return visitor.visit_block_stmt(self)

    class Expression:
        def __init__(self, expression):
            self.expression = expression

        def accept(self, visitor):
            return visitor.visit_expression_stmt(self)

    class Print:
        def __init__(self, expression):
            self.expression = expression

        def accept(self, visitor):
            return visitor.visit_print_stmt(self)

    class Var:
        def __init__(self, name, initializer):
            self.name = name
            self.initializer = initializer

        def accept(self, visitor):
            return visitor.visit_var_stmt(self)

    class If:
        def __init__(self, condition, then_branch, else_branch):
            self.condition = condition
            self.then_branch = then_branch
            self.else_branch = else_branch

        def accept(self, visitor):
            return visitor.visit_if_stmt(self)

    class While:
        def __init__(self, condition, body):
            self.condition = condition
            self.body = body

        def accept(self, visitor):
            return visitor.visit_while_stmt(self)
