from fpga.board import Board
from fpga.node import Node, NodeType

tree = Node(
    NodeType.OUTPUT,
    Node(
        NodeType.OR, 
        Node(
            NodeType.NOT, 
            Node(NodeType.INPUT),
        ),
        Node(
            NodeType.NOT, 
            Node(
                NodeType.AND, 
                Node(NodeType.INPUT),
                Node(NodeType.INPUT),
            )
        ),
    )
)

# tree = Node(
#     NodeType.OUTPUT,
#     Node(
#         NodeType.OR, 
#         Node(NodeType.INPUT),
#         Node(
#             NodeType.NOT, 
#             Node(NodeType.INPUT),
#         )
#     ),
# )

for k, v in tree.level_mapping.items():
    print(f"level={k}, nodes={v}")

board = Board(tree)