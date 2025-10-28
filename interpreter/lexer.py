from types import MappingProxyType
from .token import Tok, Token
from .errors import error
from pathlib import Path


KEYWORDS = MappingProxyType({
    #Token keywords
    'module': Tok.MODULE,
    'endmodule': Tok.ENDMODULE,
    'input': Tok.INPUT,
    'inout': Tok.INOUT,
    'wire': Tok.WIRE,
    'define': Tok.DEFINE,
    'assign': Tok.ASSIGN,
    'deassign': Tok.DEASSIGN,
    'begin': Tok.BEGIN,
    'end': Tok.END,
    'if': Tok.IF,
    'else': Tok.ELSE,
    'case': Tok.CASE,
    'endcase': Tok.ENDCASE,
    'for': Tok.FOR,
    'while': Tok.WHILE,
    'repeat': Tok.REPEAT,
    'parameter': Tok.PARAMETER,
    'function': Tok.FUNCTION,
    'endfunction': Tok.ENDFUNCTION,
    'always': Tok.ALWAYS,
    'true': Tok.TRUE,
    'false': Tok.FALSE
})

class LexerError(Exception):
    pass

#TODO: Fix Line and Col enumeration
class Lexer:
    
    def __init__(self, source: str, is_file: bool = False):

        if is_file: 
            self.source = Path(source).read_text(encoding='utf-8')
        else:
            self.source = source
        self.start = 0
        self.current = 0 #NOTE: Current represents the character TO BE consumed. Does NOT look at the just consumed character.
        self.line = 1
        self.col = 1
        self.tokens: list[Token] = []



    def scan_tokens(self) -> list:
        while not self._at_end():
            self.start = self.current
            self._scan_token()
            #print(self.tokens)
        self.tokens.append(Token(Tok.EOF, "",literal=None, line=self.line, col=self.col)) 
        return self.tokens
        


    def _at_end(self) -> bool:
        return (self.current>=len(self.source))

    
    def _advance(self) -> str:
        #Call ONLY AFTER PEEKING!!! 
        if self._at_end():
            return '\0'
        c = self.source[self.current]
        self.current += 1
        #Check for newline
        if c == '\n':
            self.col = 1
            self.line += 1
        else:
            self.col += 1
        return c
    
    def _add_token(self, type: Tok, literal: object | None = None) -> None:
        text = self.source[self.start: self.current]
        self.tokens.append(Token(type, text, self.line, self.col, literal))




    def _scan_token(self) -> None:
        c = self._advance()
        match c:
            #single character lexemes
            case '(':
                self._add_token(Tok.LPAREN)
            case ')':
                self._add_token(Tok.RPAREN)
            case '?':
                self._add_token(Tok.QMARK)
            case ':':
                self._add_token(Tok.COLON)
            case '[':
                self._add_token(Tok.LBRACKET)
            case ']':
                self._add_token(Tok.RBRACKET)
            case '}':
                self._add_token(Tok.RBRACE)
            case '{':
                self._add_token(Tok.LBRACE)
            case ';':
                self._add_token(Tok.SEMICOLON)
            case ',':
                self._add_token(Tok.COMMA)
            case '.':
                if self._peek().isdigit():
                    raise LexerError(f'Line: {self.line}, Col: {self.col} - Unexpected .')
                    
                else:
                    self._add_token(Tok.DOT)

            #Arithmetic
            case '+':
                self._add_token(Tok.PLUS)
            case '-':
                self._add_token(Tok.SUB)
            case '*':
                self._add_token(Tok.MULTIPLY)
            case '%':
                self._add_token(Tok.MOD)
            case '/':
                if self._match('/'):
                    #Ignore comments (//)
                    while(self._peek() != '\n' and not self._at_end()):
                        self._advance()
                else:
                    self._add_token(Tok.DIVIDE)

        
            #Boolean
            case '~':
                if self._match('^'):
                    self._add_token(Tok.XNOR)
                else:
                    self._add_token(Tok.NOT)
            case '&':
                if self._match('&'):
                    self._add_token(Tok.LAND)
                else:
                    self._add_token(Tok.AND)
            case '^':
                if self._match('~'):
                    self._add_token(Tok.XNOR)
                else:
                    self._add_token(Tok.XOR)
            case '|':
                if self._match('|'):
                    self._add_token(Tok.LOR)
                else:
                    self._add_token(Tok.OR)
            case '!':
                if self._match('='):
                    if self._match('='):
                        self._add_token(Tok.CNEQ)
                    else:
                        self._add_token(Tok.NEQ)
                else:
                    self._add_token(Tok.LNOT)
            case '=':
                if self._match('='):
                    if self._match('='):
                        self._add_token(Tok.CEQ)
                    else:
                        self._add_token(Tok.EQ)
                else:
                    self._add_token(Tok.ASSIGN)
            case '<':
                if self._match('='):
                    self._add_token(Tok.LTE)
                else:
                    self._add_token(Tok.LT)
            case '>':
                if self._match('='):
                    self._add_token(Tok.GTE)
                else:
                    self._add_token(Tok.GT)
            case '@':
                self._add_token(Tok.AT)
            case '#':
                self._add_token(Tok.HASH)
            case "'":
                self._number()
            case ' ':
                pass
            case '\r':
                pass
            case '\t':
                pass
            case '\n':
                pass
            case '"':
                self._string()
            case _:
                if c.isdigit():
                    self._number()

                elif c.isalpha() or c == '_':
                    self._identifier()

                else:
                    raise LexerError(f'Line: {self.line}, Col: {self.col} - Unexpected Character "{c}"')

            
    def _match(self, expected: str) -> bool:
        #conditional advance
        if self._at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True
        

    def _peek(self) -> str:
        #look at current without consuming
        if self._at_end():
            return '\0'
        return self.source[self.current]
    

    def _peekNext(self) -> str:
        if self.current+1 >= len(self.source):
            return '\0'
        return self.source[self.current+1]


    def _string(self) -> None:
        while(self._peek() != '"' and not self._at_end()):
            if self._peek() == '\n': self.line += 1; self.col = 1
            self._advance()

            if self._at_end():
                raise LexerError(f'Line: {self.line} - Unterminated string')
            
        #closing "
        self._advance()
        #Trim quotations
        text = self.source[self.start+1:self.current-1]
        self._add_token(Tok.STRING, text)


    def _identifier(self) -> None:
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()
        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, Tok.IDENT)
        self._add_token(token_type, text)

    #TODO: Clean up - maybe each number literal type is its own token? (different behaviour when parsing)
    def _number(self) -> None:
        size, signed, base = None, None, None

        while self._peek().isdigit():
            self._advance()
        
        #Check for base/sized
        if self._match("'"):
            size = self.source[self.start:self.current]
            #self.advance()
            if self._peek().lower() in {'b', 'o', 'd', 'h'}:
                print(base)
                base = self._peek()
                self._advance()
            
            #Check for signed literal
            elif self._match('s') or self._match('S'):
                signed = True
                self._advance()

            else:
                raise LexerError(f'Line: {self.line}, Col: {self.col} - "\'" must be followed by a base (b, o, d, h), or a sign (s).')
        
        if base:
            match base:
                case 'b':
                    while self._peek() in {'0', '1', 'x', 'z', '?', '_'}:
                        self._advance()
                
                case 'o':
                    while self._peek() in {'0', '1', '2', '3', '4', '5', '6',
                                            '7', 'x', 'z', '?', '_'}:
                        self._advance()
                
                case 'd':
                    while self._peek() in {'0', '1', '2', '3', '4', '5', '6',
                                            '7', '8', '9', 'x', 'z', '?', '_'}:
                        self._advance()
                case 'h':
                    while self._peek() in {'0', '1', '2', '3', '4', '5', '6',
                                            '7', '8', '9', 'a', 'b', 'c', 'd',
                                            'e', 'f', 'A', 'B', 'C', 'D',
                                            'E', 'F', 'x', 'z', '?', '_'}:
                        self._advance()
        num = self.source[self.start:self.current]
        self.tokens.append(Token(kind=Tok.NUMBER, lexeme=num, line=self.line, 
                                 col=self.col, literal=num, size=size, signed=signed, base=base))
        

        
    #Debugging
    def current_position(self) -> tuple[int, int, int]:
        #Returns current index, line, and column number.
        return (self.current, self.line, self.col)
