#Environment to holds variable declarations
from .token import Token

class Environment:

    def __init__(self):
        self.values: dict[str, object] = {} 

    def get(self, name: Token) -> object:
        if name.lexeme in self.values.keys():
            return self.values[name.lexeme]

        raise RuntimeError(f'[Line: {name.line}, Col: {name.col}] - Undefined variable {name.lexeme}.')

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return
        
        raise RuntimeError(f'[Line: {name.line}, Col: {name.col}] - Undefined variable {name.lexeme}')

