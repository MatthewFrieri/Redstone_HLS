
from collections import defaultdict
from enum import Enum
from typing import Optional


class NodeType(Enum):
    NOT = "not"
    AND = "and"
    OR = "or"
    INPUT = "input"
    OUTPUT = "output"

class Node:
    _curr_id = 0
    id_mapping: dict[int, "Node"] = {}
    level_mapping: dict[int, list["Node"]] = defaultdict(list)
    max_level = float("-inf")

    def __init__(
            self, 
            type: NodeType, 
            left: Optional["Node"] = None, 
            right: Optional["Node"] = None,
            io_id: Optional[int] = None,
        ):
        self.type = type
        self.left = left
        self.right = right
        self.io_id = io_id

        self.id = Node._curr_id
        Node.id_mapping[self.id] = self
        Node._curr_id += 1

        self.level = max(getattr(left, "level", -1), getattr(right, "level", -1)) + 1
        Node.level_mapping[self.level].append(self)
        Node.max_level = max(Node.max_level, self.level)


    def __repr__(self):
        # return f"Node(id={self.id}, lvl={self.level}, type={self.type})"
        return f"Node(id={self.id}, type={self.type}, left_id={None if self.left is None else self.left.id}, right_id={None if self.right is None else self.right.id})"

