from const import Coord2
from region_wrappper import RegionWrapper


class Gate:
    def __init__(self, width: int, length: int, inputs: list[Coord2], output: Coord2) -> None:
        self._width = width
        self._length = length
        self._inputs = inputs
        self._output = output

    def get_width(self) -> int:
        return self._width

    def get_length(self) -> int:
        return self._length

    def get_size(self) -> tuple[int, int]:
        return self._width, self._length

    def get_inputs(self) -> list[Coord2]:
        return self._inputs

    def get_output(self) -> Coord2:
        return self._output

    def build(self) -> RegionWrapper:
        raise NotImplementedError


class OR(Gate):
    def __init__(self) -> None:
        super().__init__(3, 3, [(0, 0), (2, 0)], (1, 2))

    def build(self):
        pass


class AND(Gate):
    def __init__(self) -> None:
        super().__init__(3, 4, [(0, 0), (2, 0)], (1, 3))

    def build(self):
        pass
