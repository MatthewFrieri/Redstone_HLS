HAD_ERROR = False
HAD_RUNTIME_ERROR = False
from .runtime_errors import RuntimeError_
from .token import Tok, Token
import sys


#error handling
def error(line: int | None = None, col: int | None = None, token: Token | None = None, message: str = None) -> None:
    if token:
        if token.kind == Tok.EOF:
            report(token.line, token.col, "at end", message)
        else:
            report(token.line, token.col, f'at {token.lexeme}', message)

    else:
        report(line, col, "", message)


#lmao this naming is so confusing should fix
def _RuntimeError(error: RuntimeError_) -> None:
    global HAD_RUNTIME_ERROR
    print(f'{error.message}\n [line {error.token.line}, col {error.token.col}]', file=sys.stderr)
    HAD_RUNTIME_ERROR = True

def report(line: int, col: int, where: str, message: str) -> None:
    global HAD_ERROR
    print(f"[line {line}, col {col}] Error {where}: {message}", file=sys.stderr)
    HAD_ERROR = True


