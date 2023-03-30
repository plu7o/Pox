from .token import Token
from .token_type import TokenType


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "False": TokenType.FALSE,
            "for": TokenType.FOR,
            "fn": TokenType.FN,
            "if": TokenType.IF,
            "Nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "self": TokenType.SELF,
            "True": TokenType.TRUE,
            "let": TokenType.LET,
            "while": TokenType.WHILE,
        }

    def scan_tokens(self) -> list:
        while not self.is_at_eof():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self) -> None:
        c = self.advance()
        match c:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "/":
                if self.match("*"):
                    while (
                            not self.match("*")
                            and self.peek_next() != "/"
                            and not self.is_at_eof()
                    ):
                        if self.peek() == "\n":
                            self.line += 1

                        self.advance()

                    if self.is_at_eof():
                        import pox as Pox
                        Pox.pox.lexer_error(self.line, f"Unterminated block comment found.")

                    else:
                        self.advance()

                else:
                    self.add_token(TokenType.SLASH)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
                )
            # Ignored charaters
            case "#":
                # A comment goes until the end of the line.
                while self.peek() != "\n" and not self.is_at_eof():
                    self.advance()
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case "'":
                self.string()
            case _:
                if self.is_digit(c):
                    self.number()
                elif self.is_alpha(c):
                    self.identifier()
                else:
                    import pox as Pox
                    Pox.pox.lexer_error(self.line, f'Unexpected character found: "{c}"')

    def identifier(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text = self.source[self.start: self.current]
        kind = self.keywords[text] if text in self.keywords else TokenType.IDENTIFIER

        self.add_token(kind)

    def number(self) -> None:
        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start: self.current]))

    def string(self) -> None:
        while self.peek() != "'" and not self.is_at_eof():

            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_eof():
            import pox as Pox
            Pox.pox.lexer_error(self.line, f"Unterminated string.")
            return

        # Closing '
        self.advance()

        value = self.source[self.start + 1: self.current - 1].strip("'")
        self.add_token(TokenType.STRING, value)

    def match(self, expected: str) -> bool:
        if self.is_at_eof():
            return False

        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_eof():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def is_alpha(self, c: str) -> bool:
        return c >= "a" and c <= "z" or c >= "A" and c <= "Z" or c == "_"

    def is_digit(self, c: str) -> bool:
        return c >= "0" and c <= "9"

    def is_alpha_numeric(self, c: str):
        return self.is_alpha(c) or self.is_digit(c)

    def is_at_eof(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, kind: TokenType, literal: object = None) -> None:
        text = self.source[self.start: self.current]
        self.tokens.append(Token(kind, text, literal, self.line))
