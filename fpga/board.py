import json
from fpga.node import Node, NodeType

class Board:

    def __init__(self, tree: Node):
        self.tree = tree
        self._init_board()
        self._place_inputs()
        self._place()

    def _init_board(self) -> None:
        with open("fpga/board.json", "r") as f:
            self.board = json.load(f)

        # Create sbs dict so it's a bit easier to manually make the json
        sbs = {}
        for wire_id, wire_dict in self.board["ws"].items():
            for sb_id in wire_dict["sbs"]:
                if sb_id not in sbs:
                    sbs[sb_id] = {"ws": [], "conns": {}}
                sbs[sb_id]["ws"].append(wire_id)
        self.board["sbs"] = sbs

        # Add wires to in_cbs dict so it's a bit easier to manually make the json
        for wire_id, wire_dict in self.board["ws"].items():
            in_cb_id = wire_dict["in_cb"]
            if in_cb_id is not None:
                self.board["in_cbs"][in_cb_id]["ws"].append(wire_id)

    def _place_inputs(self) -> None:
        for node in self.tree.level_mapping[0]:
            for input in self.board["inputs"].values():
                if input["node_id"] is None:
                    input["node_id"] = node.id
                    break

    def _get_free_component_id(self, component_type: str) -> str:
        for k, v in self.board[component_type].items():
            if v["node_id"] is None:
                return k

    def _apply_path(self, path: list) -> None:
        for i in range(len(path) - 1):
            prev_type, prev_id = path[i]
            curr_type, curr_id = path[i+1]
            next_type, next_id = (None, None) if i+2 >= len(path) else path[i+2]

            curr = self.board[curr_type][curr_id]

            if curr_type == "ws":
                curr["used"] = True
            elif curr_type == "sbs":
                curr["conns"][prev_id] = next_id
            elif curr_type == "in_cbs":
                curr["chosen"] = prev_id
            elif curr_type == "clbs":
                pass
            elif curr_type == "out_cbs":
                curr["chosen"] = next_id
            elif curr_type == "outputs":
                pass
            else:
                raise ValueError("Bad type={curr_type}")

    def _place(self) -> None:
        """
        Place each level of the tree by modifying the global state of `self.board`.
        """

        total_delay = 0
        level = 1
        while level <= self.tree.max_level:
            print(f"\nLEVEL={level}")
            for node in self.tree.level_mapping[level]:

                target_type = "outputs" if node.type == NodeType.OUTPUT else "clbs"
                target_id = self._get_free_component_id(target_type)
                self.board[target_type][target_id]["node_id"] = node.id

                # Wire the children of the node to its target
                delays = []
                for child in [node.left, node.right]:
                    if child is None:
                        continue
                    curr_type = "inputs" if child.type == NodeType.INPUT else "clbs"
                    curr_id = [k for k, v in self.board[curr_type].items() if v["node_id"] == child.id][0]
                    delay, path = self._dfs((None, None), (curr_type, curr_id), (target_type, target_id), 0, [])

                    if delay == float("inf"):
                        raise RuntimeError("Path impossible")            

                    delays.append(delay)  
                    print(f"delay={delay}, path={path}")
                    self._apply_path(path)

                total_delay += max(delays)
            level += 1
            print(f"\ntotal delay={total_delay}")
        
    def _dfs(
        self, 
        prev: tuple[str, str],
        curr: tuple[str, str],
        target: tuple[str, str],
        delay: int,
        path: list
    ) -> tuple[int, list]:
        """
        Recursively tries to reach the target. 
        Does not permanently modify `self.board`.
        Searches all paths for the path of least delay.
        Returns the best delay and path.
        """
        prev_type, prev_id = prev
        curr_type, curr_id = curr
        target_type, target_id = target
        new_path = path + [curr]
        
        if curr_type == "inputs":
            input = self.board[curr_type][curr_id]
            return self._dfs(curr, ("ws", input["w"]), target, delay, new_path)
        
        elif curr_type == "ws":
            w = self.board[curr_type][curr_id]
            if w["used"]:
                raise ValueError(f"DFS, starting on a wire that's already used: {curr_id}, {path}")
            w["used"] = True

            sb_ids = w["sbs"]
            if prev_type == "sbs":
                sb_ids = [sb_id for sb_id in sb_ids if sb_id != prev_id]  # filter out where we came from

            min_delay, best_path = float("inf"), None
            for sb_id in sb_ids:
                res_delay, res_path = self._dfs(curr, ("sbs", sb_id), target, delay, new_path)
                if res_delay < min_delay:
                    min_delay = res_delay
                    best_path = res_path

            in_cb_id = w["in_cb"]
            if in_cb_id is not None and target_type == "clbs":
                in_cb_available = self.board["in_cbs"][in_cb_id]["chosen"] is None
                if in_cb_available:

                    res_delay, res_path = self._dfs(curr, ("in_cbs", in_cb_id), target, delay, new_path)
                    if res_delay < min_delay:
                        min_delay = res_delay
                        best_path = res_path

            output_id = w["output"]
            if output_id is not None and target_type == "outputs":
                res_delay, res_path = self._dfs(curr, ("outputs", output_id), target, delay, new_path)
                if res_delay < min_delay:
                    min_delay = res_delay
                    best_path = res_path

            w["used"] = False
            return min_delay, best_path

        elif curr_type == "sbs":
            sb = self.board[curr_type][curr_id]
            w_ids = sb["ws"]
            w_ids = [w_id for w_id in w_ids if w_id != prev_id]  # filter out where we came from
            used_ws = [k for k, v in self.board["ws"].items() if v["used"]]
            w_ids = [w_id for w_id in w_ids if w_id not in used_ws]  # filter out where is already used

            min_delay, best_path = float("inf"), None
            for w_id in w_ids:

                if prev_id in sb["conns"]:
                    raise ValueError("DFS, sb fucked up")

                sb["conns"][prev_id] = w_id

                res_delay, res_path = self._dfs(curr, ("ws", w_id), target, delay + 1, new_path)
                if res_delay < min_delay:
                    min_delay = res_delay
                    best_path = res_path

                del sb["conns"][prev_id]

            return min_delay, best_path

        elif curr_type == "in_cbs":
            in_cb = self.board[curr_type][curr_id]
            in_cb["chosen"] = prev_id
            res = self._dfs(curr, ("clbs", in_cb["clb"]), target, delay + 1, new_path)
            in_cb["chosen"] = None
            return res

        elif curr_type == "clbs":
            if target_type == curr_type:
                if target_id == curr_id:
                    return delay, new_path
                if len(new_path) > 1:
                    return float("inf"), new_path

            clb = self.board[curr_type][curr_id]
            return self._dfs(curr, ("out_cbs", clb["out_cb"]), target, delay + 3, new_path)

        elif curr_type == "out_cbs":
            out_cb = self.board[curr_type][curr_id]
            w_ids = out_cb["ws"]
            used_ws = [k for k, v in self.board["ws"].items() if v["used"]]
            w_ids = [w_id for w_id in w_ids if w_id not in used_ws]  # filter out where is already used

            min_delay, best_path = float("inf"), None
            for w_id in w_ids:
                out_cb["chosen"] = w_id

                res_delay, res_path = self._dfs(curr, ("ws", w_id), target, delay + 1, new_path)
                if res_delay < min_delay:
                    min_delay = res_delay
                    best_path = res_path

                out_cb["chosen"] = None

            return min_delay, best_path

        elif curr_type == "outputs":
            if target_type == curr_type and target_id == curr_id:
                return delay, new_path
            return float("inf"), new_path

        raise ValueError(f"DFS, bad curr_type={curr_type}")
