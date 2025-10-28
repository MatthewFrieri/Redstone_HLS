from dataclasses import dataclass
from enum import Enum, auto

class Tok(Enum):
    #Token kinds
    
    MODULE = auto()
    ENDMODULE = auto()
    INPUT = auto()
    OUTPUT = auto()
    INOUT = auto()
    WIRE = auto()
    DEFINE = auto()
    ASSIGN = auto()
    DEASSIGN = auto()
    BEGIN = auto()
    END = auto()
    IF = auto()
    ELSE = auto()
    CASE = auto()
    ENDCASE = auto()
    FOR = auto()
    WHILE = auto()
    REPEAT = auto()
    PARAMETER = auto()
    FUNCTION = auto()
    ENDFUNCTION = auto()
    ALWAYS = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()

    

    #Literals
    IDENT = auto() #Identifier (Variable)
    NUMBER = auto()
    STRING = auto()


    #Arithmetic
    PLUS = auto() #Addtion: +
    SUB = auto() #Subtraction: -
    MULTIPLY = auto() #Multiplication: *
    DIVIDE = auto() #Division: /
    MOD = auto() #Modulus: %
    LLSHIFT = auto() #Logical left shift: <<
    LRSHIFT = auto() #Logical right shift: >>
    ALSHIFT = auto() #Arithmetic left shift: <<< #Is this needed?
    ARSHIFT = auto() #Arithmetic right shift: >>>


    #Bitwise and Reduction
    AND = auto() #Bitwise/Reduction AND: &
    OR = auto() #Bitwise/Reduction OR: |
    XOR = auto() #Bitwise/Reduction XOR: ^
    NOT = auto() #Bitwise NOT: ~
    XNOR = auto() #Bitwise/Reduction XNOR: ~^ or ^~
    #Bitwse NAND and Bitwise NOR are derived: ~(a & b), ~(a | b)


    #Logical
    LNOT = auto() #Logical NOT: !
    LAND = auto() #Logical AND: &&
    LOR = auto() #Logical OR: ||
    EQ = auto() #Equality: == (ex. 10x==10z yields True)
    NEQ = auto() #Inequality: !=
    CEQ = auto() #Case equality: === (ex. 10x===10z yields False)
    CNEQ = auto() #Case inequality: !==
    LT = auto() #Less than: <
    LTE = auto() #Less than or equal: <=
    GT = auto() #Greater than: >
    GTE = auto() #Greater than or equal: >=

    #TODO: how to parse??
    AT = auto()
    QMARK = auto() #Used in ternary conditional: cond ? a : b
    COLON = auto() #Used in ternary conditional
    #Logical NAND and Logical NOR are derived: ~(a && b), ~(a || b)


    #Other syntax stuff
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    HASH = auto()


    COMMENT = auto()
    EOF = auto()


@dataclass(frozen=True, slots=True)
class Token:
    #Abstract immutable Token class: Accepts token kind, lexeme, line number, and col number.
    kind: Tok
    lexeme: str
    line: int
    col: int
    literal: object | None = None
    #ONLY FOR NUMERIC LITERALS
    size: int | None = None
    signed: bool | None = None
    base: str | None = None