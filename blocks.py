from litemapy import BlockState

RED_WOOL = BlockState("minecraft:red_wool")
BLUE_WOOL = BlockState("minecraft:light_blue_wool")
BLACK_WOOL = BlockState("minecraft:black_wool")

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
