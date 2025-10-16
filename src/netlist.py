from enum import Enum


class NodeType(Enum):
    NOT = "NOT"
    AND = "AND"
    OR = "OR"
    XOR = "XOR"


class Node:
    def __init__(self, name: str, node_type: NodeType) -> None:
        self.name = name
        self.node_type = node_type

    def __repr__(self) -> str:
        return self.name


class Netlist:

    def __init__(self, graph: dict[Node, list[Node]]):
        self._graph = graph

    def _level_mapping(self) -> dict[Node, int]:

        levels = {}

        def _get_level_helper(node: Node):
            if node in levels:
                return
            preds = self._graph[node]

            if len(preds) == 0:
                levels[node] = 0
                return

            for pred in preds:
                _get_level_helper(pred)

            levels[node] = max([levels[pred] for pred in preds]) + 1

        for node in self._graph:
            _get_level_helper(node)

        return levels


n1 = Node("n1", NodeType.AND)
n2 = Node("n2", NodeType.AND)
n3 = Node("n3", NodeType.AND)
n4 = Node("n4", NodeType.AND)
n5 = Node("n5", NodeType.AND)
n6 = Node("n6", NodeType.AND)
n7 = Node("n7", NodeType.AND)
n8 = Node("n7", NodeType.AND)

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

print(net._level_mapping())
