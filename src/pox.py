import sys
from Lexer.lexer import Lexer
from Lexer.token import Token
from Lexer.token_type import TokenType
from Parser.expr import Expr
from Parser.ast_printer import AstPrinter
from Parser.parser import Parser


class Pox:
    hadError = False

    def main(self) -> None:
        args = sys.argv[1:]
        if len(args) > 1:
            print("Usage: Pox [script]")
            sys.exit(2)
        elif len(args) == 1:
            self.runFile(args[0])
        else:
            self.runPrompt()

    def runFile(self, file_path: str) -> None:
        with open(file_path, "r") as file:
            source = file.read()

        self.run(source)

        # Indicate an error in the exit code.
        if self.hadError:
            sys.exit(1)

    def runPrompt(self):
        print("POX Repl V.01")
        while True:
            line = input("Pox: >> ")
            if line == "exit":
                break

            self.run(line)
            self.hadError = False

    def run(self, source: str) -> None:
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        expression = parser.parse()

        if self.hadError:
            return

        print(AstPrinter().print_ast(expression))

    @classmethod
    def lexer_error(self, line: int, message: str) -> None:
        def report(line: int, where: str, message: str):
            print(f"[Line: {line}] Error {where}: {message}")
            self.hadError = True

        report(line, '', message)

    @classmethod
    def parse_error(self, token: Token, message: str) -> None:
        def report(line: int, where: str, message: str):
            print(f"[Line: {line}] Error {where}: {message}")
            self.hadError = True

        if token.token_type == TokenType.EOF:
            report(token.line, " at end", message)
        else:
            report(token.line, f' at "{token.lexeme}"', message)


if __name__ == "__main__":
    Pox().main()
