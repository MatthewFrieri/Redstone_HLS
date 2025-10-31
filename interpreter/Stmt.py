#Created from tools/GenerateAst.py
from dataclasses import dataclass
from abc import ABC, abstractmethod
from interpreter import Token
from typing import TypeVar, Generic

#Allows for subtypes to be accepted
T_co = TypeVar('T_co', covariant=True)
 
 
#Uses Expr
from .Expr import Expr




#Abstract Stmt Interface - Not to be instantiated directly
class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: 'StmtVisitor[T_co]') -> T_co:
        pass
 
 
#Abstract Visitor Interface - Not to be instantiated directly
class StmtVisitor(ABC, Generic[T_co]):
    @abstractmethod
    def visit_expression_stmt(self, node: "Expression") -> T_co: ...

    @abstractmethod
    def visit_print_stmt(self, node: "Print") -> T_co: ...

    @abstractmethod
    def visit_var_stmt(self, node: "Var") -> T_co: ...

    

 

 
@dataclass(frozen=True, slots=True)
class Expression(Stmt):
    expression: Expr
    
    def accept(self, visitor: 'StmtVisitor[T_co]') -> T_co:
        return visitor.visit_expression_stmt(self)

 
@dataclass(frozen=True, slots=True)
class Print(Stmt):
    expression: Expr
    
    def accept(self, visitor: 'StmtVisitor[T_co]') -> T_co:
        return visitor.visit_print_stmt(self)

 
@dataclass(frozen=True, slots=True)
class Var(Stmt):
    name: Token
    intializer: Expr
    
    def accept(self, visitor: 'StmtVisitor[T_co]') -> T_co:
        return visitor.visit_var_stmt(self)
