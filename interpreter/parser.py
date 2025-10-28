from .Expr import Expr, ExprVisitor, Binary, Grouping, Literal, Unary
from .token import Token, Tok
from .errors import error
from .Stmt import Stmt, StmtVisitor, Print, Expression

class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    
    def parse(self) -> list[Expr]:
        statements: list[Stmt] = []

        while not self.is_at_end():
            statements.append(self.statement())

        return statements
    

    def error(self, token: Token, message: str) -> ParseError:
        error(token=token, message=message)
        return ParseError

#Helper functions
    def statement(self) -> Stmt:
        if self.match(Tok.PRINT):
            return self.printStatement()
        return self.expressionStatement()
    
    def printStatement(self) -> Stmt:
        value = self.expression()
        self.consume(Tok.SEMICOLON, "Expected ';' after value.")
        return Print(value)
    

    def expressionStatement(self) -> Stmt:
        expr = self.expression()
        self.consume(Tok.SEMICOLON, "Expceted ';' after expression.")
        return Expression(expr)


    def match(self, *types: Tok) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
             
        return False


    def check(self, type_: Tok) -> bool:
        if self.is_at_end():
            return False

        return self.peek().kind == type_


    def advance(self) -> Token:
        if not self.is_at_end(): self.current +=1
        return self.previous()
    

    def is_at_end(self) -> bool:
        return self.peek().kind == Tok.EOF
    

    def peek(self) -> Token:
        return self.tokens[self.current]
    

    def previous(self) -> Token:
        return self.tokens[self.current - 1]




    def expression(self) -> Expr:
        return self.equality()
    
    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(Tok.NEQ, Tok.EQ):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr: 
        expr = self.term()

        while self.match(Tok.GT, Tok.GTE, Tok.LT, Tok.LTE):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr
    
    def term(self) -> Expr:
        expr = self.factor()

        while self.match(Tok.SUB, Tok.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr
    
    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(Tok.DIVIDE, Tok.MULTIPLY):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr
    
    def unary(self) -> Expr:
        if self.match(Tok.NOT, Tok.SUB):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        return self.primary()
    
    def primary(self) -> Expr:
        if self.match(Tok.FALSE): return Literal(False)
        if self.match(Tok.TRUE): return Literal(True)
        if self.match(Tok.NULL): return Literal(None)

        if self.match(Tok.NUMBER, Tok.STRING):
            return Literal(self.previous().literal)
        
        if self.match(Tok.LPAREN):
            expr = self.expression()
            self.consume(Tok.RPAREN, 'Expected ")" after expression.')
            return Grouping(expr)
        
        raise self.error(token=self.peek(), message="Unexpected Expression")



    def consume(self, type_:Tok, message: str) -> Token:
        if self.check(type_): return self.advance()
        raise self.error(self.peek(), message)
    



    



