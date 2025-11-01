from canvas import Canvas
from netlist import Netlist


class Placer:

    def __init__(self, netlist: Netlist) -> None:
        self._netlist = netlist
        self._canvas = Canvas(10, 10)

    def place_gates(self) -> None:
        levels = self._netlist.get_level_mapping()
