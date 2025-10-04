from litemapy import Region
from const import Block


class Gate:

    @staticmethod
    def And(n: int) -> Region:
        size = 2 * n - 1
        reg = Region(0, 0, 0, size, 2, 3)

        for i in range(size):
            reg[i, 0, 1] = Block.BLACK_WOOL
            reg[i, 1, 1] = Block.REDSTONE

            if i % 2 == 0:
                reg[i, 0, 0] = Block.BLACK_WOOL
                reg[i, 1, 0] = Block.TORCH

            if i == n - 1:
                reg[i, 0, 2] = Block.S_TORCH

        return reg

    @staticmethod
    def Or(n: int) -> Region:
        size = 2 * n - 1
        reg = Region(0, 0, 0, size, 2, 3)

        for i in range(size):
            reg[i, 0, 1] = Block.BLACK_WOOL
            reg[i, 1, 1] = Block.REDSTONE

            if i % 2 == 0:
                reg[i, 0, 0] = Block.BLACK_WOOL
                reg[i, 1, 0] = Block.S_REPEATER

            if i == n - 1:
                reg[i, 0, 2] = Block.BLACK_WOOL
                reg[i, 1, 2] = Block.S_REPEATER

        return reg
