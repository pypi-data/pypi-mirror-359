from typing import Dict, Optional

from feng_tools.flow.taskflow.base.Node import Node
from feng_tools.flow.taskflow.schemas.enums import NodeType


class Taskflow:
    def __init__(self, flow_id: str, name: str):
        self.flow_id = flow_id
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.start_node_id: Optional[str] = None

    def add_node(self, node: Node):
        self.nodes[node.node_id] = node
        if node.node_type == NodeType.START:
            self.start_node_id = node.node_id

    def execute(self, instance_id: str, initial_data: Dict = None):
        # 工作流执行逻辑
        pass

