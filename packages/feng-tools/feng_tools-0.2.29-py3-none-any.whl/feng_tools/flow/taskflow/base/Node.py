from abc import ABC, abstractmethod

from feng_tools.flow.taskflow.schemas.enums import NodeType, NodeStatus
from feng_tools.flow.taskflow.schemas.node_schemas import LogResult
from pydantic import BaseModel


class InputParam(BaseModel):
    pass

class OutputResult(BaseModel):
    pass

class Node(ABC):
    def __init__(self, node_id:str, name:str):
        self.node_id = node_id
        self.name=name
        self.status = NodeStatus.PENDING
        self.log_list = []

    @property
    def node_type(self) -> NodeType:
        return NodeType.NORMAL

    @abstractmethod
    def input(self, param:InputParam):
        pass

    @abstractmethod
    def output(self) -> OutputResult:
        pass

    def log(self) -> LogResult:
        return LogResult(log_list=self.log_list)

