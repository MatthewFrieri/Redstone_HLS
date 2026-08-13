from fpga.bitstream import BitstreamGenerator
from fpga.router import Router
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

router = Router(tree, "fpga/fon_3x2_3x3.json")
routed_fon = router.route()

bitstream = BitstreamGenerator(tree, routed_fon)
bitstream.generate_and_save()