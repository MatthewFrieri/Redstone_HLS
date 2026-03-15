#Created from tools/GenerateAst.py
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .token import Token
from typing import TypeVar, Generic

#Allows for subtypes to be accepted
T_co = TypeVar('T_co', covariant=True)
 
 
#Uses Expr
from .Expr import Expr




#Abstract Stmt Interface - Not to be instantiated directly
class Stmt:
    __slots__ = ()
    def accept(self, visitor: 'StmtVisitor[T_co]') -> T_co:
        pass
 
 
#Abstract Visitor Interface - Not to be instantiated directly
class StmtVisitor(Generic[T_co]):
    __slots__ = ()
    def visit_block_stmt(self, node: "Block") -> T_co: pass

    def visit_expression_stmt(self, node: "Expression") -> T_co: pass

    def visit_if_stmt(self, node: "If") -> T_co: pass

    def visit_print_stmt(self, node: "Print") -> T_co: pass

    def visit_var_stmt(self, node: "Var") -> T_co: pass

    def visit_while_stmt(self, node: "While") -> T_co: pass

    

 

 
@dataclass(frozen=True, slots=True)
class Block(Stmt):
    statements: list[Stmt]
    
    def accept(self, visitor: 'StmtVisitor[T_co]') -> T_co:
        return visitor.visit_block_stmt(self)

 
@dataclass(frozen=True, slots=True)
class Expression(Stmt):
    expression: Expr
    
    def accept(self, visitor: 'StmtVisitor[T_co]') -> T_co:
        return visitor.visit_expression_stmt(self)

 
@dataclass(frozen=True, slots=True)
class If(Stmt):
    condition: Expr
    thenBranch: Expr
    elseBranch: Expr
    
    def accept(self, visitor: 'StmtVisitor[T_co]') -> T_co:
        return visitor.visit_if_stmt(self)

 
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

 
@dataclass(frozen=True, slots=True)
class While(Stmt):
    condition: Expr
    body: Stmt
    
    def accept(self, visitor: 'StmtVisitor[T_co]') -> T_co:
        return visitor.visit_while_stmt(self)
