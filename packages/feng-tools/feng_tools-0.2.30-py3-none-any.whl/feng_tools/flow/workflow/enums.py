from feng_tools.common.enums import EnumItem, BaseEnum


class NodeType(BaseEnum):
    """工作流节点类型"""
    START = EnumItem(title="启动节点", description='工作流的起始节点，用于开启工作流', value="start")
    TASK = EnumItem(title="任务节点", description='需要执行特定任务的节点', value="task")
    DECISION = EnumItem(title='决策节点', description='根据条件选择不同分支的节点', value="decision")
    END = EnumItem(title="结束节点", description='工作流的终止节点，表示工作流结束', value="end")
    PARALLEL = EnumItem(title='并行节点', description='同时执行多个分支的节点', value="parallel")



class TaskStatus(BaseEnum):
    """任务状态"""
    PENDING = EnumItem(title="待处理", description='任务已创建但尚未开始处理', value="pending")
    IN_PROGRESS = EnumItem(title="处理中", description='任务正在处理中', value="in_progress")
    COMPLETED = EnumItem(title="已完成", description='任务已成功完成', value="completed")
    FAILED = EnumItem(title="失败", description='任务执行失败', value="failed")
    CANCELED = EnumItem(title="已取消", description='任务被取消', value="canceled")



class WorkflowStatus(BaseEnum):
    """工作流状态"""
    DRAFT = EnumItem(title="草稿", description='工作流定义已创建但尚未激活', value="draft")
    ACTIVE = EnumItem(title="激活", description='工作流已激活并可以创建实例', value="active")
    RUNNING = EnumItem(title="运行中", description='工作流实例正在运行', value="running")
    COMPLETED = EnumItem(title="已完成", description='工作流实例已成功完成', value="completed")
    FAILED = EnumItem(title="失败", description='工作流实例执行失败', value="failed")
    SUSPENDED = EnumItem(title="已暂停", description='工作流实例暂停执行', value="suspended")
    TERMINATED = EnumItem(title="已终止", description='工作流实例被手动终止', value="terminated")


class TaskPriority(BaseEnum):
    """任务优先级"""
    LOW = EnumItem(title="低", description='低优先级任务', value="low")
    MEDIUM = EnumItem(title="中", description='中优先级任务', value="medium", is_default=True)
    HIGH = EnumItem(title="高", description='高优先级任务', value="high")
    URGENT = EnumItem(title="紧急", description='紧急任务，需要立即处理', value="urgent")


class ApprovalStatus(BaseEnum):
    """审批状态"""
    PENDING = EnumItem(title="待审批", description='审批请求已提交但尚未审批', value="pending")
    APPROVED = EnumItem(title="已批准", description='审批请求已被批准', value="approved")
    REJECTED = EnumItem(title="已拒绝", description='审批请求已被拒绝', value="rejected")
    CANCELED = EnumItem(title="已取消", description='审批请求已被取消', value="canceled")


class TransitionType(BaseEnum):
    """工作流转换类型"""
    NORMAL = EnumItem(title="普通转换", description='从一个节点到另一个节点的普通转换', value="normal")
    CONDITIONAL = EnumItem(title="条件转换", description='基于条件的转换，通常从决策节点出发', value="conditional")
    DEFAULT = EnumItem(title="默认转换", description='当所有条件都不满足时的默认转换路径', value="default")
    ERROR = EnumItem(title="错误转换", description='当节点执行出错时的转换路径', value="error")
