from .Expr import Expr, ExprVisitor, Binary, Unary, Literal, Grouping
from .token import Token, Tok
import numbers #number type checking
from .runtime_errors import RuntimeError_
from .errors import _RuntimeError
from typing import Optional

class Interpreter(ExprVisitor[object]):

    def interpret(self, expression: Expr) -> None:
        try:
            value = self._evaluate(expression)
            print(self._stringify(value))
        
        except RuntimeError_ as err:
            _RuntimeError(err) 



    #helpers
    def _evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    #Allows dynamically typed boolean expressions
    def _isTruthy(self, obj: object) -> bool:
        #None and false are falsey: else, truthy
        if obj == None: return False
        if isinstance(obj, bool): return bool(obj)
        return True
    
    def _isEqual(self, a: object, b: object) -> bool:
        if (a is None) and (b is None): return True
        if (a is None): return False
        return a == b
    
    def _stringify(self, obj: object) -> str:
        if obj is None: return "None"
        if isinstance(obj, numbers.Number):
            text = str(obj)
            if text.endswith('.0'):
                text = text[0:len(text)-2]
                
            return text
        return str(obj)

    def _checkNumberOperands(self, operator: Token, *operands: object) -> None:
        for op in operands: 
            if not isinstance(op, numbers.Number):
                raise RuntimeError_(operator, "Operand(s) must be number(s).")

        return


#------------------------------------------------------------#

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value
    
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self._evaluate(expr.expression)
    
    def visit_unary_expr(self, expr: Unary) -> object:
        right = self._evaluate(expr.right)
        match expr.operator.kind:
            case Tok.SUB:
                self._checkNumberOperands(expr.operator, right)
                return -(right)
            
            case Tok.NOT:
                return not self._isTruthy(right)
            

        return None
    
    def visit_binary_expr(self, expr: Binary) -> object:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        match expr.operator.kind:
            case Tok.SUB:
                self._checkNumberOperands(expr.operator, left, right)
                return (left - right)

            case Tok.DIVIDE:
                self._checkNumberOperands(expr.operator, left, right)
                return (left / right)

            case Tok.MULTIPLY:
                self._checkNumberOperands(expr.operator, left, right)
                return (left * right)

            case Tok.PLUS:
                #Overload: Arithmetic addition and String concat
                if isinstance(left, numbers.Number) and isinstance(right, numbers.Number):
                    return float(left) + float(right)

                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                
                raise RuntimeError_(expr.operator,
                                    'Operands must be two numbers or two strings.')

            case Tok.GT:
                self._checkNumberOperands(expr.operator, left, right)
                return left > right
            
            case Tok.GTE:
                self._checkNumberOperands(expr.operator, left, right) 
                return left >= right
            
            case Tok.LT:
                self._checkNumberOperands(expr.operator, left, right)
                return left < right
            
            case Tok.LTE: 
                self._checkNumberOperands(expr.operator, left, right)
                return left <= right
            
            case Tok.NEQ:
                self._checkNumberOperands(expr.operator, left, right)
                return not self._isEqual(left, right)
            
            case Tok.EQ:
                self._checkNumberOperands(expr.operator, left, right)
                return self._isEqual(left, right)
            
        return None