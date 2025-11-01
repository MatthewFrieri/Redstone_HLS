from gates import AND, OR, Gate


class Node:
    def __init__(self, name: str, gate: Gate) -> None:
        self.name = name
        self.gate = gate

    def __repr__(self) -> str:
        return self.name


Graph = dict[Node, list[Node]]


class Netlist:

    def __init__(self, pred_graph: Graph):
        self._pred_graph = pred_graph
        self._succ_graph = self._create_succ_graph(pred_graph)

    @staticmethod
    def _create_succ_graph(pred_graph: Graph) -> Graph:
        succ_graph = {node: [] for node in pred_graph.keys()}
        for n1 in pred_graph:
            for n2 in pred_graph:
                if n1 in pred_graph[n2]:
                    succ_graph[n1].append(n2)
        return succ_graph

    def get_level_mapping(self) -> dict[Node, int]:

        levels = {}

        def _get_level_helper(node: Node):
            if node in levels:
                return
            preds = self._pred_graph[node]

            if len(preds) == 0:
                levels[node] = 0
                return

            for pred in preds:
                _get_level_helper(pred)

            levels[node] = max([levels[pred] for pred in preds]) + 1

        for node in self._pred_graph:
            _get_level_helper(node)

        return levels


n1 = Node("n1", AND())
n2 = Node("n2", OR())
n3 = Node("n3", AND())
n4 = Node("n4", OR())
n5 = Node("n5", OR())
n6 = Node("n6", AND())
n7 = Node("n7", AND())
n8 = Node("n8", OR())

graph = {}
graph[n1] = []
graph[n2] = []
graph[n3] = []
graph[n4] = [n1, n2]
graph[n5] = [n3, n4]
graph[n6] = [n5]
graph[n7] = [n2, n4, n5]
graph[n8] = [n7]
net = Netlist(graph)

print(net.get_level_mapping())
print(net._pred_graph)
print(net._succ_graph)
