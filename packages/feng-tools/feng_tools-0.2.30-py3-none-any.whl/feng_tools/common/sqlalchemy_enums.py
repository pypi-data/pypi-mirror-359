from sqlalchemy import TypeDecorator, Integer, String, Float,DECIMAL,Enum


# 自定义 SQLAlchemy 类型处理器
class EnumItemType(TypeDecorator):
    impl = Integer
    cache_ok = True

    def __init__(self, enum_type):
        super().__init__()
        self.enum_type = enum_type
        self.value_to_member = {member.value.value: member for member in enum_type}
    def process_bind_param(self, value, dialect):
        """存入数据库的值"""
        if value is None:
            return None
        if hasattr( value.value, 'value'):
            return value.value.value
        return value.value
    def process_result_value(self, value, dialect):
        """从数据库转换为枚举成员"""
        if value is None:
            return None
        return self.value_to_member.get(value)



class IntegerEnum(EnumItemType):
    impl = Integer
class StringEnum(EnumItemType):
    impl = String
class FloatEnum(EnumItemType):
    impl = DECIMAL
