from litemapy import Region
from blocks import *


class Gate:

    @staticmethod
    def And(n: int) -> Region:
        size = 2 * n - 1
        reg = Region(0, 0, 0, size, 2, 3)

        for i in range(size):
            reg[i, 0, 1] = BLACK_WOOL
            reg[i, 1, 1] = REDSTONE

            if i % 2 == 0:
                reg[i, 0, 0] = BLACK_WOOL
                reg[i, 1, 0] = TORCH

            if i == n - 1:
                reg[i, 0, 2] = S_TORCH

        return reg

    @staticmethod
    def Or(n: int) -> Region:
        size = 2 * n - 1
        reg = Region(0, 0, 0, size, 2, 3)

        for i in range(size):
            reg[i, 0, 1] = BLACK_WOOL
            reg[i, 1, 1] = REDSTONE

            if i % 2 == 0:
                reg[i, 0, 0] = BLACK_WOOL
                reg[i, 1, 0] = S_REPEATER

            if i == n - 1:
                reg[i, 0, 2] = BLACK_WOOL
                reg[i, 1, 2] = S_REPEATER

        return reg
