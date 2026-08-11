from fpga.board import Board
from fpga.node import Node, NodeType

tree = Node(
    NodeType.OUTPUT,
    Node(
        NodeType.OR, 
        Node(
            NodeType.NOT, 
            Node(NodeType.INPUT, io_id=1),
        ),
        Node(
            NodeType.NOT, 
            Node(
                NodeType.AND, 
                Node(NodeType.INPUT, io_id=0),
                Node(NodeType.INPUT, io_id=2),
            )
        ),
    ),
    io_id=2
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

# for k, v in tree.level_mapping.items():
#     print(f"level={k}, nodes={v}")

board = Board(tree, "fpga/fon_2x2_3x3.json")