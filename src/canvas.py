from enum import Enum
from const import CanvasPlacingError, Coord2
from gates import AND, OR, Gate


class Spot(Enum):
    EMPTY = "."
    FILLED = "="
    INPUT = "o"
    OUTPUT = "x"


class Canvas:

    def __init__(self, width: int, length: int) -> None:
        self._width = width
        self._length = length
        self._grid = [[Spot.EMPTY] * length for _ in range(width)]
        self._gates = {}

    def __str__(self) -> str:
        return "\n" + "\n".join([" ".join([item.value for item in row]) for row in self._grid[::-1]])

    def __getitem__(self, index: Coord2) -> str:
        x, y = index
        return self._grid[x][y]

    def _is_valid_placement(self, index: Coord2, gate: Gate) -> bool:
        x, y = index
        g_w, g_l = gate.get_size()

        if min(x, y) < 0 or (x + g_w > self._width) or (y + g_l) > self._length:
            return False

        for i in range(g_w):
            for j in range(g_l):
                new_x, new_y = x + i, y + j
                if self[new_x, new_y] != Spot.EMPTY:
                    return False
        return True

    def __setitem__(self, index: Coord2, gate: Gate) -> None:
        """Assumes the gate can be placed here."""
        x, y = index
        g_w, g_l = gate.get_size()

        for i in range(g_w):
            for j in range(g_l):
                new_x, new_y = x + i, y + j
                if (i, j) in gate.get_inputs():
                    spot_type = Spot.INPUT
                elif (i, j) == gate.get_output():
                    spot_type = Spot.OUTPUT
                else:
                    spot_type = Spot.FILLED
                self._grid[new_x][new_y] = spot_type

        self._gates[index] = gate

    def _get_valid_placements(self, gate: Gate) -> list[Coord2]:
        valid = []

        for x in range(self._width):
            for y in range(self._length):
                coord = x, y
                if self._is_valid_placement(coord, gate):
                    valid.append(coord)
        return valid


canvas = Canvas(10, 10)

print(canvas)
canvas[1, 2] = OR()
print(canvas)
canvas[7, 7] = OR()
print(canvas)
canvas[4, 4] = AND()
print(canvas)
