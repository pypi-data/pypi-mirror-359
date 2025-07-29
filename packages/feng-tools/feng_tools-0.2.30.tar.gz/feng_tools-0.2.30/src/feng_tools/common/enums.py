import enum
import typing
from typing import Optional, Any

from pydantic import BaseModel, Field


class EnumItem(BaseModel):
    # 是否是默认项
    is_default: Optional[bool] = False
    # 标题
    title: str = Field(default=None, title='枚举标题')
    description: Optional[str] = Field(default=None, title='枚举描述')
    value: Optional[str | int | float] = Field(default=None, title='枚举值')
    data_dict: Optional[dict[str, Any]] = Field(title='数据字典', default=dict())


class BaseEnum(enum.Enum):
    @classmethod
    def get_enum(cls, value: str) -> typing.Union['BaseEnum', None]:
        """根据值获取枚举项"""
        for item in cls:
            if item.value.value == value:
                return item
        return None

    @classmethod
    def get_enum_list(cls) -> list[dict[str, Any]]:
        """获取所有枚举项的列表"""
        return [item.value.model_dump() for item in cls]


class GenderTypeEnum(enum.Enum):
    """用户的性别"""
    # 值为 1 时是男性
    male = EnumItem(title='男', value=1)
    # 值为 2 时是女性
    female = EnumItem(title='女', value=2)
    # 值为 0 时是未知
    unknown = EnumItem(title='未知', value=0)

    @staticmethod
    def get_enum(value: int) -> typing.Union['GenderTypeEnum', None]:
        for item in GenderTypeEnum:
            if item.value.value == value:
                return item
        return None

    @staticmethod
    def get_enum_list() -> list[dict[str, Any]]:
        return [item.value.model_dump() for item in GenderTypeEnum]

if __name__ == '__main__':
    print(GenderTypeEnum.get_enum(2))
    print(GenderTypeEnum.get_enum_list())