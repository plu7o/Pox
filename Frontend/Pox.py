import sys
from Lexer import Lexer
from Token import Token


class Pox:
    hadError = False

    def main(self) -> None:
        args = sys.argv[1:]
        if len(args) > 1:
            print("Usage: Pox [script]")
            exit(2)
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
            exit(1)

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

        for token in tokens:
            print(token)

    @classmethod
    def error(self, line: int, message: str) -> None:
        def report(line: int, where: str, message: str):
            print(f"[Line: {line}] Error {where}: {message}")
            self.hadError = True

        report(line, "", message)


if __name__ == "__main__":
    pox = Pox()
    pox.main()
