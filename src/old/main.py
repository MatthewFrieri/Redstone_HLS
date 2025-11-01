from old.combinational_circuit import CombinationalCircuit
from const import Block
from region_wrappper import RegionWrapper


# torch = RegionWrapper(1, 1, 1)
# torch[0, 0, 0] = Block.TORCH

# redstone = RegionWrapper(1, 1, 1)
# redstone[0, 0, 0] = Block.REDSTONE

# square = RegionWrapper(2, 1, 2)
# for i in range(2):
#     square[i, 0, 1] = Block.LIGHT_BLUE_WOOL
# square.nest_region(torch, (1, 0, 0))
# square.nest_region(redstone, (0, 0, 0))

# parent = RegionWrapper(2, 2, 4)
# for i in range(2):
#     for j in range(4):
#         parent[i, 0, j] = Block.BLACK_WOOL

# parent.nest_region(square, (0, 1, 0))
# parent.nest_region(square, (0, 1, 2))

expression = ["-100", "10-0", "1-00", "101-", "1-11"]
reg = CombinationalCircuit(expression)

name = "combinational_test"
schem = reg.as_schematic(name=name)
schem.save(f"schematics/{name}.litematic")
