from Lexer.token_type import TokenType
from Lexer.token import Token
from Eval.expressions import Expr
from Eval.statements import Stmt


class Parse_error(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def expression(self) -> Expr:
        return self.assignment()

    def declaration(self) -> Stmt:
        try:
            if self.match((TokenType.LET,)):
                return self.var_declaration()

            return self.statement()

        except Parse_error as error:
            self.sync()
            return None

    def statement(self) -> Stmt:
        if self.match((TokenType.PRINT,)):
            return self.print_statement()

        if self.match((TokenType.LEFT_BRACE,)):
            return Stmt.Block(self.block())

        return self.expression_statement()

    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expected ";" after value')
        return Stmt.Print(value)

    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        initializer = None

        if self.match((TokenType.EQUAL,)):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, 'Expected ";" after variable declaration')
        return Stmt.Var(name, initializer)

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expected ";" after expression.')

    def block(self) -> list[Stmt]:
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, 'Expected "}" after block')
        return statements

    def assignment(self) -> Expr:
        expr = self.equality()

        if self.match((TokenType.EQUAL,)):
            euqals = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                name = expr.name
                return Expr.Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match((TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL)):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(
            (
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
            )
        ):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.match((TokenType.MINUS, TokenType.PLUS)):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()

        while self.match((TokenType.SLASH, TokenType.STAR)):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.match((TokenType.BANG, TokenType.MINUS)):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)

        return self.primary()

    def primary(self) -> Expr:
        if self.match((TokenType.FALSE,)):
            return Expr.Literal(False)

        if self.match((TokenType.TRUE,)):
            return Expr.Literal(True)

        if self.match((TokenType.NIL,)):
            return Expr.Literal(None)

        if self.match((TokenType.NUMBER, TokenType.STRING)):
            return Expr.Literal(self.previous().literal)

        if self.match((TokenType.IDENTIFIER,)):
            return Expr.Variable(self.peek())

        if self.match((TokenType.LEFT_PAREN,)):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, 'Expected ")" after expression.')
            return Expr.Grouping(expr)

        raise self.error(self.peek(), "Expected expression.")

    def match(self, types: tuple[TokenType]) -> bool:
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()

        raise self.error(self.peek(), message)

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1] if self.current > 0 else self.tokens[0]

    def error(self, token: Token, message: str) -> Parse_error:
        from pox import Pox

        Pox.parse_error(token, message)
        return Parse_error()

    def sync(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return

            match self.peek().token_type:
                case TokenType.CLASS:
                    return
                case TokenType.FN:
                    return
                case TokenType.LET:
                    return
                case TokenType.FOR:
                    return
                case TokenType.FOR:
                    return
                case TokenType.IF:
                    return
                case TokenType.WHILE:
                    return
                case TokenType.PRINT:
                    return
                case TokenType.RETURN:
                    return

            self.advance()
