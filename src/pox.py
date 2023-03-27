import sys
from Lexer.lexer import Lexer
from Lexer.token import Token
from Lexer.token_type import TokenType
from Eval.expressions import Expr
from Parser.ast_printer import AstPrinter
from Parser.parser import Parser
from Interpreter.interpreter import Interpreter
from Errors.runtime_error import Runtime_error


class Pox:
    def __init__(self) -> None:
        self.had_error = False
        self.had_runtime_error = False
        self.interpreter = Interpreter()

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
        if self.had_error:
            sys.exit(1)

    def runPrompt(self):
        print("POX Repl V.01")
        while True:
            line = input("Pox: >> ")
            if line == "exit":
                break

            self.run(line)
            self.had_error = False

    def run(self, source: str) -> None:
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        statements = parser.parse()

        if self.had_error:
            return

        self.interpreter.interpret(statements)

    @classmethod
    def lexer_error(self, line: int, message: str) -> None:
        def report(line: int, where: str, message: str):
            print(f"[Line: {line}] Error {where}: {message}")
            self.had_error = True

        report(line, "", message)

    @classmethod
    def parse_error(self, token: Token, message: str) -> None:
        def report(line: int, where: str, message: str):
            print(f"[Line: {line}] Error {where}: {message}")
            self.had_error = True

        if token.token_type == TokenType.EOF:
            report(token.line, " at end", message)
        else:
            report(token.line, f' at "{token.lexeme}"', message)

    @classmethod
    def runtime_error(self, error: Runtime_error):
        print(f'[Line {error.token.line}]: Runtime Error: {error.message}')
        self.had_runtime_error = True


if __name__ == "__main__":
    Pox().main()
