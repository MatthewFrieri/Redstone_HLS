#Environment to holds variable declarations
from __future__ import annotations
from .token import Token


class Environment:

    def __init__(self, enclosing: Environment |  None = None):
        self.enclosing = enclosing
        self.values: dict[str, object] = {} 

    def get(self, name: Token) -> object:
        lexeme = name.lexeme
        try:
            return self.values[lexeme]
        except KeyError:
            pass

        #Check if variable is defined in local scope recursively
        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeError(f'[Line: {name.line}, Col: {name.col}] - Undefined variable {lexeme}.')
        
    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def assign(self, name: Token, value: object) -> None:
        lexeme = name.lexeme
        if lexeme in self.values:
            self.values[lexeme] = value
            return

        if self.enclosing is not None: 
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(f'[Line: {name.line}, Col: {name.col}] - Undefined variable {lexeme}')

