"""
文件上传请求和响应的Schema定义
"""
from typing import Annotated
from fastapi import UploadFile
from pydantic import BaseModel, Field, ConfigDict

class FileUploadRequest(BaseModel):
    """文件上传请求"""
    file: Annotated[UploadFile, Field(description="文件")]
    file_uuid: Annotated[str, Field(min_length=36, max_length=36, description="文件唯一标识UUID")]
    description: Annotated[str | None, Field(default=None, description="文件描述")]
    model_config = ConfigDict(arbitrary_types_allowed=True)

class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_url: Annotated[str, Field(description="文件URL")]
