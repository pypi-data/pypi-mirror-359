from datetime import datetime
from typing import Optional, Dict

from feng_tools.flow.workflow.enums import TaskStatus


class Task:
    def __init__(self, task_id: str, name: str, assignee: str, workflow_id: str):
        self.task_id = task_id
        self.name = name
        self.assignee = assignee
        self.workflow_id = workflow_id
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.data: Dict = {}

    def start(self):
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def complete(self, data: Dict = None):
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
        if data:
            self.data = data

    def fail(self, reason: str):
        self.status = TaskStatus.FAILED
        self.updated_at = datetime.now()
        self.data["failure_reason"] = reason