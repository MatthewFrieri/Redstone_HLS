from litemapy import BlockState


Coord2 = tuple[int, int]
Coord3 = tuple[int, int, int]


class RegionNestingError(Exception):
    pass


class CanvasPlacingError(Exception):
    pass


class Block:

    AIR = BlockState("minecraft:air")

    RED_WOOL = BlockState("minecraft:red_wool")
    LIGHT_BLUE_WOOL = BlockState("minecraft:light_blue_wool")
    BLUE_WOOL = BlockState("minecraft:blue_wool")
    CYAN_WOOL = BlockState("minecraft:cyan_wool")
    BLACK_WOOL = BlockState("minecraft:black_wool")

    TARGET = BlockState("minecraft:target")
    LAMP = BlockState("minecraft:redstone_lamp")
    FLOOR_LEVER = BlockState("minecraft:lever", face="floor", facing="east")

    REDSTONE = BlockState("minecraft:redstone_wire")

    TORCH = BlockState("minecraft:redstone_torch")
    N_TORCH = BlockState("minecraft:redstone_wall_torch", facing="north")
    E_TORCH = BlockState("minecraft:redstone_wall_torch", facing="east")
    S_TORCH = BlockState("minecraft:redstone_wall_torch", facing="south")
    W_TORCH = BlockState("minecraft:redstone_wall_torch", facing="west")

    # repeaters are inverted
    N_REPEATER = BlockState("minecraft:repeater", facing="south")
    E_REPEATER = BlockState("minecraft:repeater", facing="west")
    S_REPEATER = BlockState("minecraft:repeater", facing="north")
    W_REPEATER = BlockState("minecraft:repeater", facing="east")
