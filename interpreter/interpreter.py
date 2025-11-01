from .Expr import Expr, ExprVisitor, Binary, Unary, Literal, Grouping, Variable, Assign, Logical
from .Stmt import Stmt, StmtVisitor, Expression, Print, Var, Block, If, While
from .token import Token, Tok
import numbers #number type checking
from .runtime_errors import RuntimeError_
from .errors import _RuntimeError
from .environment import Environment


class Interpreter(ExprVisitor[object], StmtVisitor[None]):

    def __init__(self):
        self.environment = Environment()

    def interpret(self, statements: list[Stmt]) -> None:

        try:
            for statement in statements:
                self._execute(statement)
        
        except RuntimeError_ as err:
            _RuntimeError(err) 



    #helpers
    def _execute(self, stmt: Stmt) -> None:
        stmt.accept(self)
        return


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
    

    def _executeBlock(self, statements: list[Stmt], environment: Environment) -> None:
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self._execute(statement)

        finally:
            self.environment = previous
        


#------------------------------------------------------------#
    #Expr
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
            
            case Tok.AND:
                self._checkNumberOperands(expr.operator, left, right)
                return int(left) & int(right)
            
            case Tok.OR:
                self._checkNumberOperands(expr.operator, left, right)
                return int(left) | int(right)
            
            case Tok.XOR:
                self._checkNumberOperands(expr.operator, left, right)
                return int(left) ^ int(right)
            
        return None
    
    def visit_variable_expr(self, expr: Variable) -> object:
        return self.environment.get(expr.name)
    
    def visit_assign_expr(self, expr: Assign) -> object:
        value = self._evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value
    
    def visit_logical_expr(self, expr: Logical) -> int:
        left = self._evaluate(expr.left)

        if expr.operator.kind == Tok.LOR:
            #short circuit: only have to check LHS
            if self._isTruthy(left):
                return 1

        elif expr.operator.kind == Tok.LAND:
            if not self._isTruthy(left):
                return 0
            
        right = self._evaluate(expr.right)

        if expr.operator.kind == Tok.LXOR:
            return int(self._isTruthy(left) != self._isTruthy(right))

        if self._isTruthy(right):
            return 1
        
        return 0

    #Stmt
    def visit_block_stmt(self, stmt: Block) -> None:
        new_env = Environment(self.environment)
        self._executeBlock(stmt.statements, new_env)
        return


    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)
        return
    
    def visit_if_stmt(self, stmt: If) -> None:
        #Evaluate truthy on conditional
        if self._isTruthy(self._evaluate(stmt.condition)):
            self._execute(stmt.thenBranch)

        #No else Branch -> None
        elif stmt.elseBranch is not None:
            self._execute(stmt.elseBranch)
        else:
            return

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))
        return
    
    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.intializer != None:
            value = self._evaluate(stmt.intializer)
        
        self.environment.define(stmt.name.lexeme, value)
        return 
    
    def visit_while_stmt(self, stmt: While) -> None:
        condition = stmt.condition
        while self._isTruthy(self._evaluate(condition)):
            self._execute(stmt.body)
        
        return
