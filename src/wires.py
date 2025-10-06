from const import *
from region_wrappper import RegionWrapper


class Wire:

    @staticmethod
    def east(n: int, block: Block) -> RegionWrapper:
        reg = RegionWrapper(n, 2, 1)
        for i in range(n):
            reg[i, 0, 0] = block
            if i % 16 == 0:
                reg[i, 1, 0] = Block.E_REPEATER
            else:
                reg[i, 1, 0] = Block.REDSTONE
        return reg

    @staticmethod
    def west(n: int, block: Block) -> RegionWrapper:
        reg = RegionWrapper(n, 2, 1)
        for i in range(n):
            x = n - i - 1
            reg[x, 0, 0] = block
            if i % 16 == 0:
                reg[x, 1, 0] = Block.W_REPEATER
            else:
                reg[x, 1, 0] = Block.REDSTONE
        return reg

    @staticmethod
    def south(n: int, block: Block) -> RegionWrapper:
        reg = RegionWrapper(1, 2, n)
        for i in range(n):
            reg[0, 0, i] = block
            if i % 16 == 0:
                reg[0, 1, i] = Block.S_REPEATER
            else:
                reg[0, 1, i] = Block.REDSTONE
        return reg

    @staticmethod
    def north(n: int, block: Block) -> RegionWrapper:
        reg = RegionWrapper(1, 2, n)
        for i in range(n):
            z = n - i - 1
            reg[0, 0, z] = block
            if i % 16 == 0:
                reg[0, 1, z] = Block.N_REPEATER
            else:
                reg[0, 1, z] = Block.REDSTONE
        return reg

    @staticmethod
    def south_bridge(n: int, block: Block) -> RegionWrapper:
        reg = RegionWrapper(1, 3, n)
        for i in range(n):
            if i == 0 or i == n - 1:
                reg[0, 0, i] = block
                reg[0, 1, i] = Block.REDSTONE
            else:
                reg[0, 1, i] = block
                reg[0, 2, i] = Block.REDSTONE
        return reg
