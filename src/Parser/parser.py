from Lexer.token_type import TokenType
from Lexer.token import Token
from .expr import Expr


class Parse_error(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self):
        try:
            return self.expression()
        except Parse_error:
            return None

    def expression(self) -> Expr:
        return self.equality()

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

        if self.match((TokenType.LEFT_PAREN,)):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after expression')
            return Expr.Grouping(expr)

        raise self.error(self.peek(), "Expect expression")

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
