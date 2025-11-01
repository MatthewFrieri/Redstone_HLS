from const import Block
from old.gates import Gate
from wires import Wire
from region_wrappper import RegionWrapper


class CombinationalCircuit(RegionWrapper):

    def __init__(self, expression: list[str]):
        """Builds a standard form expression.
        Example expression: ['001', '1-0', '100']"""

        if len(expression) == 0:
            raise ValueError("Expression must not be empty.")

        self.n_inputs = len(expression[0])
        n_operands = len("".join(expression).replace("-", ""))

        width = n_operands * 2 + 1
        height = 4
        length = self.n_inputs * 2 + 2 + 3 + 1

        super().__init__(width, height, length)

        self.build_inputs_and_outputs()
        self.build_wires()
        self.build_bridges(expression)
        self.build_negations_and_buffers(expression)
        self.build_and_gates(expression)

    def build_inputs_and_outputs(self) -> None:
        for i in range(self.n_inputs):
            self[0, 1, 2 * i] = Block.LAMP
            self[0, 2, 2 * i] = Block.FLOOR_LEVER
        self[0, 1, self.max_z()] = Block.LAMP

    def build_wires(self) -> None:
        input_wire = Wire.east(self.width - 1, Block.LIGHT_BLUE_WOOL)
        output_wire = Wire.west(self.width - 1, Block.LIGHT_BLUE_WOOL)
        for i in range(self.n_inputs):
            self.nest_region(input_wire, (1, 0, 2 * i))
        self.nest_region(output_wire, (1, 0, self.max_z()))

    def build_bridges(self, expression: list[str]) -> None:
        bridges = []
        for i in range(self.n_inputs):
            bridge = Wire.south_bridge(2 * (self.n_inputs - i) - 1, Block.BLUE_WOOL)
            bridges.append(bridge)

        x = self.max_x()
        for term in expression:
            for i, operand in enumerate(term):
                if operand == "-":
                    continue
                self.nest_region(bridges[i], (x, 1, i * 2 + 1))
                x -= 2

    def build_negations_and_buffers(self, expression: list[str]) -> None:
        negation = RegionWrapper(1, 2, 2)
        buffer = RegionWrapper(1, 2, 2)

        for reg in (negation, buffer):
            reg[0, 0, 0] = Block.CYAN_WOOL
            reg[0, 0, 1] = Block.CYAN_WOOL
            reg[0, 1, 1] = Block.REDSTONE

        negation[0, 1, 0] = Block.S_TORCH
        buffer[0, 1, 0] = Block.S_REPEATER

        x = self.max_x()
        for term in expression:
            for operand in term:
                if operand == "-":
                    continue
                reg = buffer if operand == "1" else negation
                self.nest_region(reg, (x, 0, self.n_inputs * 2))
                x -= 2

    def build_and_gates(self, expression: list[str]) -> None:
        and_gates = {}

        x = self.max_x() + 2
        for term in expression:
            n_operands = len(term.replace("-", ""))
            x -= n_operands * 2

            if n_operands not in and_gates:
                and_gates[n_operands] = Gate.south_and(n_operands)

            and_gate = and_gates[n_operands]
            self.nest_region(and_gate, (x, 1, self.n_inputs * 2 + 2))
