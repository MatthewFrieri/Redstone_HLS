HAD_ERROR = False
from .token import Tok, Token
import sys


#error handling
def error(line: int | None, col: int | None, token: Token | None, message: str) -> None:
    if token:
        if token.kind == Tok.EOF:
            report(token.line, token.col, "at end", message)
        else:
            report(token.line, token.col, f'at {token.lexeme}', message)

    else:
        report(line, col, "", message)

def report(line: int, col: int, where: str, message: str) -> None:
    global HAD_ERROR
    print(f"[line {line}, col {col}] Error {where}: {message}", file=sys.stderr)
    HAD_ERROR = True