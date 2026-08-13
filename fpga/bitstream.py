from fpga.node import Node, NodeType
from fpga.const import CDir

class BitstreamGenerator:
    """
    Generates the minecraft commands to place the necessary redstone to implement the `routed_fon`.
    The command stream should be executed from the reference point of the minecraft fpga board.
    """

    CELL_WIDTH = 13
    CELL_HEIGHT = 12
    CHANNEL_GAP = 2

    def __init__(self, tree: Node, routed_fon: dict):
        self.tree = tree
        self.fon = routed_fon
        self.commands = []

    def generate_and_save(self):
        self._generate_cbs_bitstream()
        self._generate_clbs_bitstream()
        self._generate_sbs_bitstream()

        with open("bitstream.mcfunction", "w") as f:
            f.writelines(self.commands)

    def _set_air(self, x: int, y: int, z: int) -> None:
        self.commands.append(f"setblock ~{x} ~{y} ~{z} air\n")

    def _set_dust(self, x: int, y: int, z: int) -> None:
        self.commands.append(f"setblock ~{x} ~{y} ~{z} redstone_wire\n")

    def _set_repeater(self, x: int, y: int, z: int, cdir: CDir) -> None:
        self.commands.append(f"setblock ~{x} ~{y} ~{z} repeater[facing={CDir.get_opposite(cdir).value}]\n")

    def _get_metadata(self) -> tuple[int, int, int]:
        meta = self.fon["meta"]
        return meta["width"], meta["height"], meta["channel_size"]

    def _get_wire_cdir_relative_to_sb(self, sb_id: int, w_id: int) -> CDir:
        width, height, size = self._get_metadata()

        if w_id == sb_id:
            return CDir.EAST
        elif w_id == sb_id - size:
            return CDir.WEST
        elif w_id == sb_id + size * width:
            return CDir.SOUTH
        elif w_id == sb_id - size * (width + 1):
            return CDir.NORTH
        return CDir.EAST  # Must be an output wire

    def _generate_cbs_bitstream(self) -> None:
        width, height, size = self._get_metadata()

        for i in range(width):
            for j in range(height):

                # in_cbs
                in_cb_id = 2*(i + width * j)
                in_cb = self.fon["in_cbs"][str(in_cb_id)]
                chosen = in_cb["chosen"]
                if chosen is not None:
                    x = self.CELL_WIDTH*i + 1
                    z = self.CELL_HEIGHT*j + 6
                    for level in range(size):
                        y = -self.CHANNEL_GAP*level - 2
                        if level == in_cb["ws"].index(chosen):
                            self._set_repeater(x, y, z, CDir.EAST)
                        else:
                            self._set_air(x, y, z)

                in_cb_id += 1
                in_cb = self.fon["in_cbs"][str(in_cb_id)]
                chosen = in_cb["chosen"]
                if chosen is not None:
                    x = self.CELL_WIDTH*i + 6
                    z = self.CELL_HEIGHT*j + 11
                    for level in range(size):
                        y = -self.CHANNEL_GAP*level - 2
                        if level == in_cb["ws"].index(chosen):
                            self._set_repeater(x, y, z, CDir.NORTH)
                        else:
                            self._set_air(x, y, z)

                # out_cbs
                out_cb_id = i + width * j
                out_cb = self.fon["out_cbs"][str(out_cb_id)]
                chosen = out_cb["chosen"]
                if chosen is not None:
                    x = self.CELL_WIDTH*i + 12
                    z = self.CELL_HEIGHT*j + 6
                    for level in range(size):
                        y = -self.CHANNEL_GAP*level - 2
                        if level == out_cb["ws"].index(chosen):
                            self._set_repeater(x, y, z, CDir.EAST)
                        else:
                            self._set_air(x, y, z)

    def _generate_clbs_bitstream(self) -> None:
        width, height, size = self._get_metadata()
        
        for i in range(width):
            for j in range(height):

                clb_id = i + width * j
                clb = self.fon["clbs"][str(clb_id)]
                if clb["node_id"] is None:
                    continue

                x = self.CELL_WIDTH*i + 9
                z = self.CELL_HEIGHT*j + 2
                y = -5

                # Fill all with air first
                for k in range(4):
                    self._set_air(x, y+2*k, z)

                gate_type = self.tree.id_mapping[clb["node_id"]].type
                if gate_type == NodeType.AND:
                    self._set_dust(x, y, z+6)
                if gate_type == NodeType.OR:
                    self._set_dust(x, y, z+2)
                    self._set_dust(x, y, z+4)
                    self._set_dust(x, y, z+6)
                if gate_type == NodeType.NOT:
                    self._set_dust(x, y, z)
                    in_cb_0_used = False
                    for in_cb in self.fon["in_cbs"].values():
                        if in_cb["chosen"] is not None:
                            in_cb_0_used = True
                            break
                    if in_cb_0_used:
                        self._set_dust(x, y, z+4)
                    else:
                        self._set_dust(x, y, z+2)

    def _generate_sbs_bitstream(self) -> None:
        width, height, size = self._get_metadata()

        for i in range(width + 1):
            for j in range(height + 1):
                x = self.CELL_WIDTH*i
                z = self.CELL_HEIGHT*j
                for level in range(size):
                    sb_id = size * (j * (2*width+1) + i) + level
                    sb = self.fon["sbs"][str(sb_id)]
                    y = -self.CHANNEL_GAP*level - 2

                    # Fill all with air first
                    self._set_air(x, y, z)
                    self._set_air(x-1, y-1, z)
                    self._set_air(x+1, y-1, z)
                    for delta_x, delta_z in [
                        (-2, -2), (-2, 2), (2, -2), (2, 2),
                        (-1, -2), (-1, 2), (1, -2), (1, 2),
                        (-2, -1), (2, -1), (-2, 1), (2, 1),
                    ]:
                        self._set_air(x + delta_x, y, z + delta_z)

                    for k, v in sb["conns"].items():
                        k, v = int(k), int(v)
                        from_dir = self._get_wire_cdir_relative_to_sb(sb_id, k)
                        to_dir = self._get_wire_cdir_relative_to_sb(sb_id, v)
                        opposite_from_dir = CDir.get_opposite(from_dir)

                        if from_dir == CDir.NORTH:
                            if to_dir == CDir.EAST:
                                self._set_dust(x+1, y, z-2)
                                self._set_dust(x+2, y, z-2)
                                self._set_repeater(x+2, y, z-1, opposite_from_dir)
                            elif to_dir == CDir.SOUTH:
                                self._set_repeater(x, y, z, to_dir)
                            elif to_dir == CDir.WEST:
                                self._set_dust(x-1, y, z-2)
                                self._set_dust(x-2, y, z-2)
                                self._set_repeater(x-2, y, z-1, opposite_from_dir)

                        elif from_dir == CDir.EAST:
                            if to_dir == CDir.NORTH:
                                self._set_dust(x+2, y, z-1)
                                self._set_dust(x+2, y, z-2)
                                self._set_repeater(x+1, y, z-2, opposite_from_dir)
                            elif to_dir == CDir.SOUTH:
                                self._set_dust(x+2, y, z+1)
                                self._set_dust(x+2, y, z+2)
                                self._set_repeater(x+1, y, z+2, opposite_from_dir)
                            elif to_dir == CDir.WEST:
                                self._set_dust(x-1, y-1, z)
                                self._set_repeater(x+1, y-1, z, to_dir)

                        elif from_dir == CDir.SOUTH:
                            if to_dir == CDir.NORTH:
                                self._set_repeater(x, y, z, to_dir)
                            elif to_dir == CDir.EAST:
                                self._set_dust(x+1, y, z+2)
                                self._set_dust(x+2, y, z+2)
                                self._set_repeater(x+2, y, z+1, opposite_from_dir)
                            elif to_dir == CDir.WEST:
                                self._set_dust(x-1, y, z+2)
                                self._set_dust(x-2, y, z+2)
                                self._set_repeater(x-2, y, z+1, opposite_from_dir)

                        elif from_dir == CDir.WEST:
                            if to_dir == CDir.NORTH:
                                self._set_dust(x-2, y, z-1)
                                self._set_dust(x-2, y, z-2)
                                self._set_repeater(x-1, y, z-2, opposite_from_dir)
                            elif to_dir == CDir.EAST:
                                self._set_dust(x+1, y-1, z)
                                self._set_repeater(x-1, y-1, z, to_dir)
                            elif to_dir == CDir.SOUTH:
                                self._set_dust(x-2, y, z+1)
                                self._set_dust(x-2, y, z+2)
                                self._set_repeater(x-1, y, z+2, opposite_from_dir)