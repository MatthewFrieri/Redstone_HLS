from .Expr import Expr, ExprVisitor, Binary, Grouping, Literal, Unary, Variable, Assign, Logical, Call
from .token import Token, Tok
from .errors import error
from .Stmt import Stmt, StmtVisitor, Print, Expression, Var, Block, If, While
from .environment import Environment

class ParseError(Exception):
    pass


class Parser:
    '''
    This Parser uses Recursive Descent, along with an LL(1) Context Free Grammar. The grammar is defined in the grammar.cfg file. 
    Each expression is defined recursively, in order of lowest to highest "precedence". Higher precedence operations and expressions take priority
    and are evaluated before lower precedence. Since the grammar rules are defined in terms of higher precedence, they are recursively called until
    the given token suites the rule. Thus, the base case is Primary.
    The LL(1) means that the parser must lookahead a minimum of one token in order to parse an expression fully with no backtracking. See the example below.
    Example: 1 + 2 * -3;
    Tokens: [1, +, 2, *, -, 3, ;]

    Start:
    Program
        statement
            exprStmt
                expression
                    equality
                        comparison
                            term
                                factor
                                    unary
                                        primary: token[0] defined as Literal.
                                    token[1] in ( ~ | - )? no -> move up
                                token[1] in ( * | / )? no -> move up
                            token[1] in ( + | - )? yes -> left factor = token[0], operation = token[1]. 
                            Parse token[2].
                                        primary: token[2] defined as Literal.
                                    token[3] in ( ~ | - )? no -> move up
                                token[3] in ( * | / )? yes -> left unary = token[2], operation = token[3].
                                Parse token[4].
                                    token[4] in ( ~ | - )? yes -> operation = token[4].
                                    Parse token[5].
                                        primary: token[5] defined as Literal.
                                        Token[6] = ";", terminate.
                                
                                    
    Thus, the final parsed expression is:
    (+ 1 
        ( * 2
            ( - 3))
    Or, in a tree:
          +
         / \
        1   *
           / \
          2   3
    
    The precedence ordering allows for certain operations ( /, * ) to take place before others ( +, - ).
    For further reading: 
        https://en.wikipedia.org/wiki/Recursive_descent_parser - Recursive Descent
        https://en.wikipedia.org/wiki/Context-free_grammar - CFG (Context Free Grammar)
        https://en.wikipedia.org/wiki/LL_parser - LL parsers
        https://www.youtube.com/watch?v=ENKT0Z3gldE - Grammars and Recursive Descent Parsing
    '''

    #TODO: Refactor bruh this is so unreadable
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0



    def parse(self) -> list[Expr]:
        statements: list[Stmt] = []

        while not self.is_at_end():
            statements.append(self.declaration())

        return statements
    

    def error(self, token: Token, message: str) -> ParseError:
        error(token=token, message=message)
        return ParseError


    def synchronize(self) -> None:
        self.advance()
        while not self.is_at_end():
            if self.previous().kind == Tok.SEMICOLON:
                return
            
            match self.peek().kind:
                case Tok.FUNCTION: ...
                case Tok.VAR: ...
                case Tok.FOR: ...
                case Tok.IF: ...
                case Tok.WHILE: ...
                case Tok.PRINT: ...
            
            self.advance()

    def statement(self) -> Stmt:
        if self.match(Tok.IF):
            return self.ifStatement()
        if self.match(Tok.PRINT):
            return self.printStatement()
        if self.match(Tok.BEGIN):
            return Block(self.block())
        if self.match(Tok.WHILE):
            return self.whileStatement()
        if self.match(Tok.FOR):
            return self.forStatement()

        return self.expressionStatement()
    
    def printStatement(self) -> Stmt:  
        value = self.expression()
        self.consume(Tok.SEMICOLON, "Expected ';' after value.")
        return Print(value)
    

    def varDeclaration(self) -> Stmt:
        name = self.consume(Tok.IDENT, "Expected Variable name")
        initializer: Expr = None
        if self.match(Tok.EQUAL):
            initializer=self.expression()
        self.consume(Tok.SEMICOLON, "Expected ';' after variable declaration.")
        return Var(name, initializer)
    

    def expressionStatement(self) -> Stmt:
        expr = self.expression()
        self.consume(Tok.SEMICOLON, "Expceted ';' after expression.")
        return Expression(expr)

    #Helper functions
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

    def declaration(self) -> Stmt:
        try:
            if self.match(Tok.VAR):
                return self.varDeclaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None
        
    def block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while (not self.check(Tok.END)) and (not self.is_at_end()):
            statements.append(self.declaration())
        
        self.consume(Tok.END, 'Expected END keyword after block.')
        return statements
    

    def ifStatement(self) -> Stmt:
        self.consume(Tok.LPAREN, "Expected '(' after if condition.")
        condition = self.expression()
        self.consume(Tok.RPAREN, "Expected ')' after if condition.")

        thenBranch = self.statement()
        elseBranch = None
        if self.match(Tok.ELSE):
            elseBranch = self.statement()

        return If(condition, thenBranch, elseBranch)

    def whileStatement(self) -> Stmt:
        #Not expression?
        self.consume(Tok.LPAREN, "Expected '(' after While.)")
        condition = self.expression()
        self.consume(Tok.RPAREN, "Expected ')' after While.")
        body = self.statement()
        return While(condition, body)
    
    def forStatement(self) -> Stmt:
        self.consume(Tok.LPAREN, "Expected '(' after For.")
        if self.match(Tok.SEMICOLON):
            initializer = None
        elif self.match(Tok.VAR):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()

        condition = None
        if not self.check(Tok.SEMICOLON):
            condition = self.expression()
        self.consume(Tok.SEMICOLON, "Expected ';' after loop conditional")

        increment = None
        if not self.check(Tok.RPAREN):
            increment = self.expression()
        self.consume(Tok.RPAREN, "Expected ')' after For.")

        body = self.statement()

        #Syntactic Sugar: for loop is While w/ increment
        if increment is not None:
            body = Block([body, Expression(increment)])
        
        #No condition -> infinite loop
        if condition is None: condition = Literal(True)
        body = While(condition, body)

        if initializer is not None:
                body = Block([initializer, body]) 


        return body

    
#------------------------------------------------

    def expression(self) -> Expr:
        return self.assignment()
    
    def assignment(self) -> Expr:
        expr = self.logical_or()
        if self.match(Tok.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            
            error(token=equals, message='Invalid assignment target.')

        return expr
    
    def logical_or(self) -> Expr:
        expr = self.logical_xor()
        while self.match(Tok.LOR):
            operator = self.previous()
            right = self.logical_xor()
            expr = Logical(expr, operator, right)

        return expr
    
    def logical_xor(self) -> Expr:
        expr = self.logical_and()
        while self.match(Tok.LXOR):
            operator = self.previous()
            right = self.logical_and()
            expr = Logical(expr, operator, right)

        return expr

    def logical_and(self) -> Expr:
        expr = self.bit_or()
        while self.match(Tok.LAND):
            operator = self.previous()
            right = self.bit_or()
            expr = Logical(expr, operator, right)
        
        return expr

    def bit_or(self) -> Expr:
        expr = self.bit_xor()
        while self.match(Tok.OR):
            operator = self.previous()
            right = self.bit_xor()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def bit_xor(self) -> Expr:
        expr = self.bit_and()
        while self.match(Tok.XOR):
            operator = self.previous()
            right = self.bit_and()
            expr = Binary(expr, operator, right)

        return expr
    
    def bit_and(self) -> Expr:
        expr = self.equality()
        while self.match(Tok.AND):
            operator = self.previous()
            right = self.equality()
            expr = Binary(expr, operator, right)

        return expr
    
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
        
        return self.call()
    
    def call(self) -> Expr:
        expr = self.primary()
        while True:
            if self.match(Tok.LPAREN):
                expr = self.finishCall(expr)
            else:
                break
        
        return expr

    def finishCall(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []

        if not self.check(Tok.RPAREN):
            arguments.append(self.expression())
            while self.match(Tok.COMMA):
                arguments.append(self.expression())
                if len(arguments) >= 255:
                    error(token=self.peek(), message="Cannot have more than 255 arguments.")

        paren = self.consume(Tok.RPAREN, "Expected ')' after function call")

        return Call(callee, paren, arguments)
    
    def primary(self) -> Expr:
        if self.match(Tok.FALSE): return Literal(False)
        if self.match(Tok.TRUE): return Literal(True)
        if self.match(Tok.NULL): return Literal(None)

        if self.match(Tok.NUMBER, Tok.STRING):
            return Literal(self.previous().literal)

        if self.match(Tok.IDENT):
            return Variable(self.previous())

        if self.match(Tok.LPAREN):
            expr = self.expression()
            self.consume(Tok.RPAREN, 'Expected ")" after expression.')
            return Grouping(expr)
        
        raise self.error(token=self.peek(), message="Unexpected Expression")




    def consume(self, type_:Tok, message: str) -> Token:
        if self.check(type_): return self.advance()
        raise self.error(self.peek(), message)
    



    



