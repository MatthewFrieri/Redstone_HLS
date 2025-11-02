from .token import Token, Tok
from .Expr import Expr, ExprVisitor, Literal, Grouping, Variable, Binary, Assign, Unary
from .Stmt import Stmt, StmtVisitor, Expression, Var
#from ..src.gates import Gate
from .environment import Environment
from .runtime_errors import RuntimeError_
from .errors import _RuntimeError

class NetlistGenerator(ExprVisitor[object], StmtVisitor[None]):
    
    def __init__(self):
        self.environment = Environment()

        #All variables in seen not in driven
        self.inputs: set[str] = set()
        #All variables in driven
        self.outputs: set[str] = set()
        self.nets: set[str] = set()
        self.gates = {
            'AND', 'OR', 'XOR', 'NOT'
        }
        self.netlist: list[str] = []

        self.temp_id = 0
        self.inst_id = 0

        #All variables that have been assigned (initializer != None | in assignment statement)
        self.driven: set[str] = set()
        #All variables that have been declared, but not assigned; can be used in RHS of assignment.
        self.seen: set[str] = set()

        #At visit_var_stmt: If initializer is not None, push name.literal. If empty, target is temp else self.target, pop after
        self.target_stack: list[str | None] = []

    def create_netlist(self, statements: list[Stmt]):
        try:
            for statement in statements:
                self._execute(statement)
            self.inputs = {x for x in self.seen if x not in self.driven}
            self.outputs = {x for x in self.driven if x not in self.seen}
            self.nets = {f't{x}' for x in range(1, self.temp_id + 1)}
            self.nets = self.nets | self.outputs | self.inputs
            print(f'In: {self.inputs}\nOut: {self.outputs}\n\nOperations:')
            for net in self.netlist:
                print(f'{net}') 
            print(f'\nNets: {self.nets}') 

        except RuntimeError_ as err:
            _RuntimeError(err)


    #Helpers
    def _newtemp(self) -> str:
        self.temp_id += 1
        return f't{self.temp_id}'

    def _newinst(self) -> str:
        self.inst_id += 1
        return f'u{self.inst_id}'

    def _get_target_name(self) -> str:
        if len(self.target_stack) == 0: 
            return self._newtemp()
        top = self.target_stack[-1]
        if top is None:
            return self._newtemp()
        return top


    def _is_truthy(self, obj: object) -> bool:
        if obj is None: return False
        if isinstance(obj, bool): return bool(obj)
        return True

    def _execute(self, stmt: Stmt) -> None:
        stmt.accept(self)
        return

    def _evaluate(self, expr: Expr, target=None) -> object:
        #Targets are added ONLY in variable declaration(if there exists an initializer), or in variable assignment.
        #We append the target to the target stack, and then evaluate the expression where the output is the target.
        #Pop the target off stack after evaluation.
        self.target_stack.append(target)
        try:
            return expr.accept(self)
        finally:
            self.target_stack.pop()

    def _add_operation(self, left, operation: Tok, right, target) -> None:
        op = ''
        match operation:
            case Tok.XOR: op = 'XOR'
            case Tok.AND: op = 'AND'
            case Tok.OR: op = 'OR'
            case Tok.NOT: op = 'NOT'
        
        if right is None:
            self.netlist.append(f'{self._newinst()}: {op} A = {left}, Y = {target}')
        
        else:
            self.netlist.append(f'{self._newinst()}: {op} A = {left}, B = {right}, Y = {target}')
    
#--------------------STMT-------------------

    def visit_var_stmt(self, stmt: Var) -> None:
        name = stmt.name.lexeme
        value = None

        if stmt.intializer is not None:
            value = self._evaluate(stmt.intializer, target=name)
            self.driven.add(name)

        self.environment.define(stmt.name.lexeme, value)
        return

    
    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.execute(stmt)
        return

    #To be implemented
    def visit_block_stmt(self, node):
        pass
    def visit_if_stmt(self, node):
        pass
    def visit_print_stmt(self, node):
        pass
    def visit_while_stmt(self, node):
        pass

#--------------------EXPR-------------------
    def visit_literal_expr(self, expr: Literal) -> object:
        return self._is_truthy(expr.value)
    
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self._evaluate(expr.expression, target=None)
    
    def visit_binary_expr(self, expr: Binary) -> object:
        #Children get no target
        A = self._evaluate(expr.left, target=None)
        B = self._evaluate(expr.right, target=None)
        Y = self._get_target_name()

        self._add_operation(left = A, operation = expr.operator.kind, right = B, target = Y)
        return Y
    
    def visit_unary_expr(self, expr: Unary) -> object:
        #Children get no target
        A = self._evaluate(expr.right, target=None)
        Y = self._get_target_name()

        self._add_operation(right=None, operation=expr.operator.kind, left=A, target=Y)
        return Y
    
    def visit_variable_expr(self, expr: Variable) -> object:
        name = expr.name.lexeme
        self.seen.add(name)
        return name
        

    def visit_assign_expr(self, expr: Assign) -> object:
        name = expr.name.lexeme
        self.driven.add(name)
        value = self._evaluate(expr.value, target=name)
        self.environment.assign(name, value)
        return value

    #To be implemented
    def visit_call_expr(self, node):
        pass
    def visit_logical_expr(self, node):
        pass