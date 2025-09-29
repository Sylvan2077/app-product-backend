from pydantic import BaseModel, Field
from src.status_code import StatusCode

class BaseResponse(BaseModel):
    """
    V3 Admin Vite 模板要求的统一响应格式
    """
    code: int = Field(examples=0, title="业务状态码")
    data: dict = Field(examples={}, title="响应数据")
    msg: str = Field(examples="success", title="响应消息")

    def __init__(self, code: int = 200, data: dict = None, msg: str = "success"):
        if data is None:
            data = {}   
        super().__init__(code=code, data=data, msg=msg)  
        self.code = code
        self.data = data
        self.msg = msg
    
    @staticmethod
    def success(status_code: StatusCode = StatusCode.SUCCESS, data: dict = None):
        if data is None:
            data = {}
        return BaseResponse(code=status_code.code, data=data, msg=status_code.msg)   
    
    @staticmethod
    def fail(status_code: StatusCode = StatusCode.FAILL, data: dict = None, error_msg: str = None):
        if data is None:
            data = {}
        if error_msg is None:
            return BaseResponse(code=status_code.code, data=data, msg=status_code.msg)
        else:
            return BaseResponse(code=status_code.code, data=data, msg=error_msg)
