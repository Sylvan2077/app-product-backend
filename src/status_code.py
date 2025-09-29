
from enum import Enum


class StatusCode(Enum):
    SUCCESS = (200, "请求成功")
    FAILL = (400, "请求失败")

@property
def code(self):
    return self.value[0]
@property
def msg(self):
    return self.value[1]