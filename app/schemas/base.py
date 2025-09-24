from typing import Generic, TypeVar, Optional, Any, Union
from pydantic import BaseModel, Field

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """统一响应基类"""
    code: int = Field(default=0, description="状态码，0表示成功")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    
    @classmethod
    def success(cls, data: T = None, msg: str = "操作成功") -> 'BaseResponse[T]':
        """创建成功响应的便捷方法"""
        return cls(code=0, msg=msg, data=data)
    
    @classmethod
    def error(cls, code: int, msg: str) -> 'BaseResponse[None]':
        """创建错误响应的便捷方法"""
        return cls(code=code, msg=msg, data=None)