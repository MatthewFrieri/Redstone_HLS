#Environment to holds variable declarations
from __future__ import annotations
from .token import Token


class Environment:

    def __init__(self, enclosing: Environment |  None = None):
        self.enclosing = enclosing
        self.values: dict[str, object] = {} 

    def get(self, name: Token) -> object:
        lexeme = name.lexeme
        env = self
        while env is not None:
            if lexeme in env.values:
                return env.values[lexeme]
            env = env.enclosing

        raise RuntimeError(f'[Line: {name.line}, Col: {name.col}] - Undefined variable {lexeme}.')
        
    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def assign(self, name: Token, value: object) -> None:
        lexeme = name.lexeme
        env = self
        while env is not None:
            if lexeme in env.values:
                env.values[lexeme] = value
                return
            env = env.enclosing

        raise RuntimeError(f'[Line: {name.line}, Col: {name.col}] - Undefined variable {lexeme}')

