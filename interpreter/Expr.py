#Created from GenerateAst.py
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from .token import Token

T_co = TypeVar('T_co', covariant=True)
 
 
class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: 'ExprVisitor[T_co]') -> T_co:
        pass
 
 
class ExprVisitor(ABC, Generic[T_co]):
    @abstractmethod
    def visit_binary_expr(self, node: "Binary") -> T_co: ...

    @abstractmethod
    def visit_grouping_expr(self, node: "Grouping") -> T_co: ...

    @abstractmethod
    def visit_literal_expr(self, node: "Literal") -> T_co: ...

    @abstractmethod
    def visit_unary_expr(self, node: "Unary") -> T_co: ...

    

 

 
@dataclass(frozen=True, slots=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr
    
    def accept(self, visitor: 'ExprVisitor[T_co]') -> T_co:
        return visitor.visit_binary_expr(self)

 
@dataclass(frozen=True, slots=True)
class Grouping(Expr):
    expression: Expr
    
    def accept(self, visitor: 'ExprVisitor[T_co]') -> T_co:
        return visitor.visit_grouping_expr(self)

 
@dataclass(frozen=True, slots=True)
class Literal(Expr):
    value: object
    
    def accept(self, visitor: 'ExprVisitor[T_co]') -> T_co:
        return visitor.visit_literal_expr(self)

 
@dataclass(frozen=True, slots=True)
class Unary(Expr):
    operator: Token
    right: Expr
    
    def accept(self, visitor: 'ExprVisitor[T_co]') -> T_co:
        return visitor.visit_unary_expr(self)
    

    
