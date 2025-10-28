from .Expr import Expr, ExprVisitor, Binary, Unary, Literal, Grouping
from .token import Token, Tok

class AstPrinter(ExprVisitor[str]):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)
    

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        parts = ['(', name]
        for expr in exprs:
            parts.append(' ')
            parts.append(expr.accept(self))
        
        parts.append(')')
        return ''.join(parts)
    

    def visit_unary_expr(self, expr: Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)
    

    def visit_binary_expr(self, expr: Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self._parenthesize('group', expr.expression)
    

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value==None: return "None"

        return str(expr.value) 
    


#test
if __name__ == '__main__':
    expr = Binary(left=Unary(Token(Tok.SUB, '-', None, 1), (Literal(123))),
                  operator=Token(Tok.MULTIPLY, '*', None, 1),
                  right=Grouping(Literal(45.67)) 
                  )
    print(AstPrinter().print(expr))