#R edstone
#H igh
#L evel
#S ynthesis

#RDT, RC, RHC, 

import sys
from pathlib import Path
from .errors import HAD_ERROR, HAD_RUNTIME_ERROR
from .token import Tok, Token
from .parser import Parser
from .lexer import Lexer
#from .old.AstPPrinter import AstPrinter
#from .interpreter import Interpreter
from .netlistPrinter import NetlistGenerator


#interpreter = Interpreter()
net = NetlistGenerator()


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
    if HAD_RUNTIME_ERROR:
        sys.exit(70)


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
    parser = Parser(tokens=tokens)
    statements = parser.parse()
    
    if HAD_ERROR: return
    #interpreter.interpret(statements)
    net.create_netlist(statements)
if __name__ == '__main__':
    file = sys.argv[1:]
    #bruh
    if str(file[0])[-4:] != '.rhc':
            raise TypeError("Filetype must be .rhc")
    main(file)