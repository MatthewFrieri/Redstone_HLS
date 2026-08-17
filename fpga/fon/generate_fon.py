import json


class GenerateFON:
    """
    Builds the FPGA Object Notation (fon) for a v1 architecture board of any size.
    This contains 3 bit channels, 2 bit input / 1 bit output CLBs,
    and disjoint switch blocks.
    """

    SIZE = 3

    def __init__(self, width: int, height: int, n_inputs: int, n_outputs: int):
        self.width = width
        self.height = height
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        if self.n_inputs > self.width * self.SIZE:
            raise ValueError("Too many inputs")
        if self.n_outputs > self.height * self.SIZE:
            raise ValueError("Too many outputs")

    def _get_n_wires(self) -> int:
        return self.SIZE * ((2 * self.width + 1) * self.height + self.width)

    def _init_board(self) -> dict:
        return {
            "meta": {
                "width": self.width,
                "height": self.height,
                "n_inputs": self.n_inputs,
                "n_outputs": self.n_outputs,
                "channel_size": self.SIZE,
            },
            "inputs": {},
            "outputs": {},
            "sbs": {},
            "in_cbs": {},
            "clbs": {},
            "out_cbs": {},
        }

    def _generate_ws(self, board: dict) -> None:

        n_wires = self._get_n_wires()
        board["ws"] = {
            str(i): {"source": None, "sbs": [], "in_cb": None, "output": None}
            for i in range(n_wires)
        }

        # Populate sbs field for all wires
        for i in range(self.width + 1):
            for j in range(self.height + 1):
                is_right = i == self.width
                is_left = i == 0
                is_bottom = j == self.height
                is_top = j == 0

                sb = self.SIZE * (j * (2*self.width+1) + i)
                ws = []
                if not is_right:
                    ws.append(sb)
                if not is_left:
                    ws.append(sb - self.SIZE)
                if not is_bottom:
                    ws.append(sb + self.SIZE * self.width)
                if not is_top:
                    ws.append(sb - self.SIZE * (self.width + 1))

                for w in ws:
                    for k in range(self.SIZE):
                        board["ws"][str(w+k)]["sbs"].append(str(sb+k))

    def _generate_cbs_and_clbs(self, board: dict) -> None:

        for i in range(self.width):
            for j in range(self.height):
                n = i + self.width * j
                sn = str(n)

                board["clbs"][sn] = {"out_cb": sn, "node_id": None}

                out_cb_w = self.SIZE * ((self.width + 1) * (j+1) + n)
                board["out_cbs"][sn] = {
                    "ws": [str(out_cb_w + k) for k in range(self.SIZE)],
                    "chosen": []
                }

                in_cb_0_w = self.SIZE * ((self.width + 1) * (j+1) + n-1)
                board["in_cbs"][str(2*n)] = {
                    "ws": [str(in_cb_0_w + k) for k in range(self.SIZE)],
                    "chosen": None,
                    "clb": sn
                }
                in_cb_1_w = self.SIZE * ((self.width + 1) * (j+2) + n-1)
                board["in_cbs"][str(2*n+1)] = {
                    "ws": [str(in_cb_1_w + k) for k in range(self.SIZE)],
                    "chosen": None,
                    "clb": sn
                }

                for in_cb, w_start in zip([2*n, 2*n+1], [in_cb_0_w, in_cb_1_w]):
                    for offset in range(self.SIZE):
                        w = w_start + offset
                        board["ws"][str(w)]["in_cb"] = str(in_cb)

    def _generate_inputs_outputs(self, board: dict) -> None:
        n_wires = self._get_n_wires()

        # Generate inputs
        for i in range(self.n_inputs):
            n = n_wires + i
            sb = n - self.SIZE * self.width
            board["ws"][str(n)] = {"source": None, "sbs": [str(sb)], "in_cb": None, "output": None}
            board["inputs"][str(i)] = {"w": str(n)}

        # Generate outputs
        for i in range(self.n_outputs):
            n = n_wires + self.n_inputs + i
            sb = self.SIZE * ((2*self.width+1) * (i // 3) + self.width) + i % 3
            board["ws"][str(n)] = {"source": None, "sbs": [str(sb)], "in_cb": None, "output": str(i)}
            board["outputs"][str(i)] = {"node_id": None}

    def _generate_sbs(self, board: dict) -> None:
        for wire_id, wire_dict in board["ws"].items():
            for sb_id in wire_dict["sbs"]:
                if sb_id not in board["sbs"]:
                    board["sbs"][sb_id] = {"ws": [], "conns": {}}
                board["sbs"][sb_id]["ws"].append(wire_id)

    def generate_and_save(self) -> None:

        board = self._init_board()
        self._generate_ws(board)
        self._generate_cbs_and_clbs(board)
        self._generate_inputs_outputs(board)
        self._generate_sbs(board)

        filename = f"fon_{self.width}x{self.height}_{self.n_inputs}x{self.n_outputs}.json"
        with open(filename, "w") as f:
            json.dump(board, f)

GenerateFON(3,2,3,3).generate_and_save()