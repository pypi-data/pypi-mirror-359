from feng_tools.common.enums import EnumItem, BaseEnum


class NodeType(BaseEnum):
    """任务流节点类型"""
    NORMAL = EnumItem(title="普通节点", description='普通节点', value="normal")


class NodeStatus(BaseEnum):
    """节点状态"""
    PENDING = EnumItem(title="待处理", description='任务已创建但尚未开始处理', value="pending")
    IN_PROGRESS = EnumItem(title="处理中", description='任务正在处理中', value="in_progress")
    COMPLETED = EnumItem(title="已完成", description='任务已成功完成', value="completed")
    FAILED = EnumItem(title="失败", description='任务执行失败', value="failed")
    CANCELED = EnumItem(title="已取消", description='任务被取消', value="canceled")

class HttpMethod(BaseEnum):
    """HTTP请求方法"""
    GET = EnumItem(title="GET请求", description='获取资源，不应有副作用', value="get")
    POST = EnumItem(title="POST请求", description='提交数据，可能创建新资源或触发操作', value="post")
    PUT = EnumItem(title="PUT请求", description='更新资源，替换整个资源', value="put")
    DELETE = EnumItem(title="DELETE请求", description='删除指定资源', value="delete")
    HEAD = EnumItem(title="HEAD请求", description='与GET相同但不返回响应体，用于获取元数据', value="head")
    PATCH = EnumItem(title="PATCH请求", description='部分更新资源', value="patch")
    OPTIONS = EnumItem(title="OPTIONS请求", description='获取目标资源支持的通信选项', value="options")
    TRACE = EnumItem(title="TRACE请求", description='沿着请求-响应链执行消息环回测试', value="trace")
    CONNECT = EnumItem(title="CONNECT请求", description='建立到目标资源标识的服务器的隧道', value="connect")