import json
from fpga.src.node import Node, NodeType

class Router:

    def __init__(self, fon_path: str):
        self._init_board(fon_path)
        self._validate()

    def _init_board(self, fon_path: str) -> None:
        with open(fon_path, "r") as f:
            self.board = json.load(f)

    def _validate(self) -> None:
        for node in Node.level_mapping[0]:
            if node.io_id >= self.board["meta"]["n_inputs"]:
                raise ValueError(f"Expression tree has INPUT with io_id out of bounds: {node.io_id}")
        for node in Node.level_mapping[Node.max_level]:
            if node.io_id >= self.board["meta"]["n_outputs"]:
                raise ValueError(f"Expression tree has OUTPUT with io_id out of bounds: {node.io_id}")
        n_gates = sum(len(Node.level_mapping[i]) for i in range(1, Node.max_level))
        if n_gates > len(self.board["clbs"]):
            raise ValueError(f"Too many gates in expression tree: {n_gates}")

    def route(self) -> dict:
        """
        Place each level of the tree by modifying the global state of `self.board`.
        """

        total_delay = 0
        level = 1
        while level <= Node.max_level:
            print(f"\nLEVEL={level}")
            for node in Node.level_mapping[level]:

                if node.type == NodeType.OUTPUT:
                    target_type = "outputs"
                    target_id = str(node.io_id)
                else:
                    target_type = "clbs"
                    target_id = self._get_free_clb_id()

                self.board[target_type][target_id]["node_id"] = node.id

                # Wire the children of the node to its target
                delays = []
                for child in [node.left, node.right]:
                    if child is None:
                        continue

                    if child.type == NodeType.INPUT:
                        curr_type = "inputs"
                        curr_id = str(child.io_id)
                    else:
                        curr_type = "clbs"
                        curr_id = [k for k, v in self.board[curr_type].items() if v["node_id"] == child.id][0]

                    
                    delay, path = self._dfs((None, None), (curr_type, curr_id), (curr_type, curr_id), (target_type, target_id), 0, [])
                    if delay == float("inf"):
                        raise RuntimeError("Path impossible")            

                    delays.append(delay)  
                    print(f"delay={delay}, path={path}")
                    self._apply_path(path)

                total_delay += max(delays)
            level += 1
            print(f"\ntotal delay={total_delay}")
        return self.board
        
    def _get_free_clb_id(self) -> str:
        for k, v in self.board["clbs"].items():
            if v["node_id"] is None:
                return k

    def _get_unused_w_ids(self) -> list[str]:
        return [k for k, v in self.board["ws"].items() if not v.get("_used")]

    @staticmethod
    def _sb_add_conn(sb: dict, from_id: str, to_id: str) -> None:
        if from_id in sb["conns"]:
            sb["conns"][from_id].append(to_id)
        else:
            sb["conns"][from_id] = [to_id]

    @staticmethod
    def _sb_remove_conn(sb: dict, from_id: str, to_id: str) -> None:
        sb["conns"][from_id].remove(to_id)
        if len(sb["conns"][from_id]) == 0:
            del sb["conns"][from_id]

    def _apply_path(self, path: list) -> None:
        source = path[0]
        for i in range(1, len(path)):
            prev_type, prev_id = path[i-1]
            curr_type, curr_id = path[i]
            next_type, next_id = (None, None) if i+1 >= len(path) else path[i+1]
            if curr_type == "clbs":
                source = path[i]

            curr = self.board[curr_type][curr_id]

            if curr_type == "ws":
                if curr["source"] is not None and curr["source"] != source:
                    raise ValueError("Wire source got overwritten")
                curr["source"] = source
            elif curr_type == "sbs":
                self._sb_add_conn(curr, prev_id, next_id)
            elif curr_type == "in_cbs":
                curr["chosen"] = prev_id
            elif curr_type == "clbs":
                pass
            elif curr_type == "out_cbs":
                curr["chosen"].append(next_id)
            elif curr_type == "outputs":
                pass
            else:
                raise ValueError(f"Bad type={curr_type}")

    def _get_cost(self, curr: tuple[str, str], source: tuple[str, str]) -> int:
        curr_type, curr_id = curr

        delay_cost = {
            "inputs": 0,
            "ws": 0,
            "sbs": 1,
            "in_cbs": 1,
            "out_cbs": 1,
            "clbs": 3,
            "outputs": 0,
        }

        length_cost = 0
        if curr_type == "ws":
            w = self.board[curr_type][curr_id]
            if w["source"] != source:
                length_cost = 1

        return delay_cost[curr_type] + length_cost
        
    def _dfs(
        self, 
        prev: tuple[str, str],
        curr: tuple[str, str],
        source: tuple[str, str],
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
        new_delay = delay + self._get_cost(curr, source)

        min_delay, best_path = float("inf"), None
        def dfs_helper(new_curr_type: str, new_curr_id: str):
            nonlocal min_delay, best_path
            res_delay, res_path = self._dfs(curr, (new_curr_type, new_curr_id), source, target, new_delay, new_path)
            if res_delay < min_delay:
                min_delay = res_delay
                best_path = res_path

        if curr_type == "inputs":
            input = self.board[curr_type][curr_id]
            dfs_helper("ws", input["w"])
        
        elif curr_type == "ws":
            w = self.board[curr_type][curr_id]
            w["_used"] = True

            sb_ids = w["sbs"]
            if prev_type == "sbs":
                sb_ids = [sb_id for sb_id in sb_ids if sb_id != prev_id]  # filter out where we came from
            for sb_id in sb_ids:
                dfs_helper("sbs", sb_id)

            in_cb_id = w["in_cb"]
            if in_cb_id is not None and target_type == "clbs":
                if self.board["in_cbs"][in_cb_id]["chosen"] is None:
                    dfs_helper("in_cbs", in_cb_id)

            output_id = w["output"]
            if output_id is not None and target_type == "outputs":
                dfs_helper("outputs", output_id)

            del w["_used"]

        elif curr_type == "sbs":
            sb = self.board[curr_type][curr_id]
            w_ids = sb["ws"]
            w_ids = [w_id for w_id in w_ids if w_id in self._get_unused_w_ids()]
            for w_id in w_ids:
                w_source = self.board["ws"][w_id]["source"]
                if not w_source or w_source == source:
                    self._sb_add_conn(sb, prev_id, w_id)
                    dfs_helper("ws", w_id)
                    self._sb_remove_conn(sb, prev_id, w_id)

        elif curr_type == "in_cbs":
            in_cb = self.board[curr_type][curr_id]
            in_cb["chosen"] = prev_id
            dfs_helper("clbs", in_cb["clb"])
            in_cb["chosen"] = None

        elif curr_type == "out_cbs":
            out_cb = self.board[curr_type][curr_id]
            w_ids = out_cb["ws"]
            w_ids = [w_id for w_id in w_ids if w_id in self._get_unused_w_ids()]  

            for w_id in w_ids:
                w_source = self.board["ws"][w_id]["source"]
                if not w_source or w_source == source:
                    out_cb["chosen"].append(w_id)
                    dfs_helper("ws", w_id)
                    out_cb["chosen"].remove(w_id)

        elif curr_type == "clbs":
            if target_type == curr_type:
                if target_id == curr_id:
                    return new_delay, new_path
                if len(new_path) > 1:
                    return float("inf"), new_path

            clb = self.board[curr_type][curr_id]
            dfs_helper("out_cbs", clb["out_cb"])

        elif curr_type == "outputs":
            if target_type == curr_type and target_id == curr_id:
                return new_delay, new_path
            return float("inf"), new_path

        return min_delay, best_path
