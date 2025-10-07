"""
云存储服务统一返回类
"""

from pydantic import BaseModel, Field


class CloudUploadResponse(BaseModel):
    """云存储上传响应"""

    success: bool = Field(description="是否成功")
    object_key: str | None = Field(default=None, description="对象键")
    filename: str | None = Field(default=None, description="文件名")
    etag: str | None = Field(default=None, description="ETag")
    url: str | None = Field(default=None, description="访问URL")
    error: str | None = Field(default=None, description="错误信息")


class CloudDeleteResponse(BaseModel):
    """云存储删除响应"""

    success: bool = Field(description="是否成功")
    object_key: str | None = Field(default=None, description="对象键")
    error: str | None = Field(default=None, description="错误信息")


class CloudUrlResponse(BaseModel):
    """云存储URL响应"""

    success: bool = Field(description="是否成功")
    url: str | None = Field(default=None, description="访问URL")
    expires: int | None = Field(default=None, description="过期时间（秒）")
    error: str | None = Field(default=None, description="错误信息")
