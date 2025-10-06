from const import Block
from region_wrappper import RegionWrapper


class Gate:

    @staticmethod
    def south_and(n: int) -> RegionWrapper:
        size = 2 * n - 1
        reg = RegionWrapper(size, 2, 3)

        for i in range(size):
            reg[i, 0, 1] = Block.BLACK_WOOL
            reg[i, 1, 1] = Block.REDSTONE

            if i % 2 == 0:
                reg[i, 0, 0] = Block.TARGET
                reg[i, 1, 0] = Block.TORCH

            if i == n - 1:
                reg[i, 0, 2] = Block.S_TORCH

        return reg
