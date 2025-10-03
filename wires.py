from litemapy import Region
from blocks import *


class Wire:

    @staticmethod
    def Straight(n: int) -> Region:
        reg = Region(0, 0, 0, 1, 2, n)

        for i in range(n):
            reg[0, 0, i] = BLUE_WOOL
            reg[0, 1, i] = REDSTONE

        return reg
