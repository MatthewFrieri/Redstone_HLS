from pathlib import Path

#Tool used to generate expr.py

'''
Visitor Pattern:

Actions performed on specific expressions could be implemeneted in seperate classes, however said classes would need to 
know which expression subclasses they must act on. Since subclasses dont behave like enums, a switch case statement is not viable.
This would require a series of if statements, however this would be very slow and not scalable.

Alternatively, Implementing each action within a single Expr class could work, however this violates the open/close principle, as implementation of 
new functions requires changes to multiple nodes.
The visitor pattern defines abstract visitor objects to be performed on by specific subclasses. When an operation is called,
the visitor will accept the operation and dispatch it to a parent ExprVisitor abstract class, to perform the operation. This ensures scalability
and readability.

This tool is used to generate the nodes and base interfaces needed for the visitor pattern. Each node is implemented as a dataclass
that is frozen and slots=True, to enforce read-only behaviour and improve memory performance. For additional readability, a covariant type variable 
is used to statically enforce types, such that they are consistent within operations and subclasses.
'''



HEADER = '''\
#Created from tools/GenerateAst.py
from dataclasses import dataclass
from abc import ABC, abstractmethod
from interpreter import Token
from typing import TypeVar, Generic

#Allows for subtypes to be accepted
T_co = TypeVar('T_co', covariant=True)
'''

BASE_CLASS = '''\
#Abstract {Base} Interface - Not to be instantiated directly
class {Base}(ABC):
    @abstractmethod
    def accept(self, visitor: '{Base}Visitor[T_co]') -> T_co:
        pass
'''


VISITOR_INTERFACE = '''\
#Abstract Visitor Interface - Not to be instantiated directly
class {Base}Visitor(ABC, Generic[T_co]):
    {Methods}
'''


NODE_CLASS = '''\
@dataclass(frozen=True, slots=True)
class {Name}({Base}):
    {Fields}
    def accept(self, visitor: '{Base}Visitor[T_co]') -> T_co:
        return visitor.{Visit_name}(self)
'''

EXPR_DEPENDANT = '''\
#Uses Expr
from .Expr import Expr


'''


def define_ast(
        #out_directory: str,
        base: str,
        definitions: dict[str, list[str]],
        dependant: bool = False):

    methods = ''
    nodes = []
    for className, params in definitions.items():
        field = ''


        visitName = f'visit_{className.lower()}_{base.lower()}'
        methods += f'@abstractmethod\n    def {visitName}(self, node: "{className}") -> T_co: ...\n\n    '
        for param in params:
            field += (': '.join(param.split())) + '\n    '

        nodes.append(NODE_CLASS.format(Name=className,Base=base, Fields=field, Visit_name=visitName))

    if dependant: 
        code =f'{HEADER} \n \n{EXPR_DEPENDANT}\n\n{BASE_CLASS.format(Base=base)} \n \n{VISITOR_INTERFACE.format(Base=base, Methods=methods)}\n \n' 
    else:
        code = f'{HEADER} \n \n{BASE_CLASS.format(Base=base)} \n \n{VISITOR_INTERFACE.format(Base=base, Methods=methods)}\n \n'
    for node in nodes:
        code += '\n \n' + node
    
    output_path = Path(__file__).resolve().parent.parent

    with open(f'{output_path}/{base}.py', 'w') as f:
        f.write(code)



definitions = {
    'Binary' : ['left Expr', 'operator Token', 'right Expr'],
    'Grouping' : ['expression Expr'],
    'Literal' : ['value object'],
    'Unary' : ['operator Token', 'right Expr']
}

statements = {
    "Expression" : ['expression Expr'],
    "Print" : ["expression Expr"]
}


if __name__ == '__main__':
    define_ast(base='Stmt', definitions=statements, dependant=True)
