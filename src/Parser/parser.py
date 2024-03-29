from Lexer.token_type import TokenType
from Lexer.token import Token
from Eval.expressions import Expr
from Eval.statements import Stmt
from Errors.runtime_error import Runtime_error


class Parse_error(Runtime_error):
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
            if self.match(TokenType.FN):
                return self.function("function")
            if self.match(TokenType.LET):
                return self.var_declaration()

            return self.statement()

        except Parse_error as error:
            self.sync()
            return None

    def statement(self) -> Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()

        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.PRINT):
            return self.print_statement()
        
        if self.match(TokenType.RETURN):
            return self.return_statement()

        if self.match(TokenType.WHILE):
            return self.while_statement()

        if self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())

        return self.expression_statement()

    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, 'Expected "(" after "for".')
        initializer = None

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.LET):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, 'Expected ";" loop condition')

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after for clauses.')

        body = self.statement()

        if increment != None:
            body = Stmt.Block([body, Stmt.Expression(increment)])

        if condition == None:
            condition = Expr.Literal(True)
        body = Stmt.While(condition, body)

        if initializer != None:
            body = Stmt.Block([initializer, body])

        return body

    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, 'Expected "(" after "if".')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'Expected ")" after if condition.')

        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return Stmt.If(condition, then_branch, else_branch)

    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expected ";" after value')
        return Stmt.Print(value)

    def return_statement(self) -> Stmt:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, 'Expected ";" after return value.')
        return Stmt.Return(keyword, value)

    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        initializer = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, 'Expected ";" after variable declaration')
        return Stmt.Var(name, initializer)

    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, 'Expect "(" after "while".')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'Expected ")" after condition')
        body = self.statement()

        return Stmt.While(condition, body)

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expected ";" after expression.')
        return Stmt.Expression(expr)

    def function(self, kind: str) -> Stmt.Function:
        name = self.consume(TokenType.IDENTIFIER, f'Expect {kind} name.')
        self.consume(TokenType.LEFT_PAREN, f'Expected "(" after {kind} name.')
        parameters = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can'have more than 255 parameters.")
                
                parameters.append(self.consume(TokenType.IDENTIFIER, 'Expected parameter name.'))
                
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, 'Expected ")" after parameters.')
        self.consume(TokenType.LEFT_BRACE, 'Expected "{" before %s body}' % (kind))
        body = self.block()

        return Stmt.Function(name, parameters, body)


    def block(self) -> list[Stmt]:
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, 'Expected "}" after block')
        return statements

    def assignment(self) -> Expr:
        expr = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                name = expr.name
                return Expr.Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def logical_or(self) -> Expr:
        expr = self.logical_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def logical_and(self) -> Expr:
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)

        return self.call()

    def finish_call(self, callee: Expr) -> Expr:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break

        paren = self.consume(TokenType.RIGHT_PAREN, 'Expected ")" after arguments.')

        return Expr.Call(callee, paren, arguments)

    def call(self) -> Expr:
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break

        return expr

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Expr.Literal(False)

        if self.match(TokenType.TRUE):
            return Expr.Literal(True)

        if self.match(TokenType.NIL):
            return Expr.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return Expr.Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, 'Expected ")" after expression.')
            return Expr.Grouping(expr)

        raise self.error(self.peek(), "Expected expression.")

    def match(self, *types) -> bool:
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        self.error(self.peek(), message)

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        t = self.peek().token_type
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
        return self.tokens[self.current - 1]

    def error(self, token: Token, message: str) -> Parse_error:
        import pox as Pox

        Pox.pox.parse_error(token, message)
        raise Parse_error()

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
