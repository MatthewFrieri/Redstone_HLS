#Created from tools/GenerateAst.py
from dataclasses import dataclass
from abc import ABC, abstractmethod
from interpreter import Token
from typing import TypeVar, Generic

#Allows for subtypes to be accepted
T_co = TypeVar('T_co', covariant=True)
 
 
#Abstract Expr Interface - Not to be instantiated directly
class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: 'ExprVisitor[T_co]') -> T_co:
        pass
 
 
#Abstract Visitor Interface - Not to be instantiated directly
class ExprVisitor(ABC, Generic[T_co]):
    @abstractmethod
    def visit_assign_expr(self, node: "Assign") -> T_co: ...

    @abstractmethod
    def visit_binary_expr(self, node: "Binary") -> T_co: ...

    @abstractmethod
    def visit_grouping_expr(self, node: "Grouping") -> T_co: ...

    @abstractmethod
    def visit_literal_expr(self, node: "Literal") -> T_co: ...

    @abstractmethod
    def visit_unary_expr(self, node: "Unary") -> T_co: ...

    @abstractmethod
    def visit_logical_expr(self, node: "Logical") -> T_co: ...

    @abstractmethod
    def visit_variable_expr(self, node: "Variable") -> T_co: ...

    

 

 
@dataclass(frozen=True, slots=True)
class Assign(Expr):
    name: Token
    value: Expr
    
    def accept(self, visitor: 'ExprVisitor[T_co]') -> T_co:
        return visitor.visit_assign_expr(self)

 
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

 
@dataclass(frozen=True, slots=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr
    
    def accept(self, visitor: 'ExprVisitor[T_co]') -> T_co:
        return visitor.visit_logical_expr(self)

 
@dataclass(frozen=True, slots=True)
class Variable(Expr):
    name: Token
    
    def accept(self, visitor: 'ExprVisitor[T_co]') -> T_co:
        return visitor.visit_variable_expr(self)
