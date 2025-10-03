from gates import Gate
from wires import Wire

# reg = Wire.Straight(10)
# reg = Gate.And(4)
reg = Gate.Or(8)

name = "or_gate"
schem = reg.as_schematic(name=name)
schem.save(f"schematics/{name}.litematic")
