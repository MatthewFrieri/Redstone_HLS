#R edstone
#H igh
#L evel
#S ynthesis

import sys
from pathlib import Path
from .errors import HAD_ERROR
from .token import Tok, Token
from .parser import Parser
from .lexer import Lexer
from .AstPPrinter import AstPrinter


def main(argv: list[str]) -> None:
    if len(argv) > 1:
        print("Useage: rhls [script]")
        sys.exit(64) #cmd line error

    elif len(argv) == 1:
        run_file(argv[0]) #Run script file

    else:
        run_prompt() #Start REPL


def run_file(path: str) -> None:
    global HAD_ERROR
    source = Path(path).read_text(encoding='utf-8')
    run(source)
    if HAD_ERROR:
        sys.exit(65) #data error


def run_prompt() -> None:
    global HAD_ERROR
    try:
        while True:
            line = input("> ")
            run(line)
            HAD_ERROR = False #Keep REPL open after error
    except (KeyboardInterrupt):
        print()


def run(source: str) -> None:


    lex=Lexer(source, is_file=False)
    tokens = lex.scan_tokens()
    print("tokens: ", [t.lexeme for t in tokens])
    p = Parser(tokens=tokens)
    expression = p.parse()
    print('AST:\n')
    for expr in expression:
        print(expr)
    print('\n')
    if HAD_ERROR: return
    print('Pretty Printer Output:\n')
    for expr in expression:
        print(AstPrinter().print(expr))


if __name__ == '__main__':
    main(['source.txt'])
