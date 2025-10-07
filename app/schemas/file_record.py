"""
文件上传请求和响应的Schema定义
"""
from enum import Enum
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

class CallType(str, Enum):
    """通话类型枚举"""
    CALL_IN = "callIn"
    CALL_OUT = "callOut"

class CallRecord(BaseModel):
    """通话记录信息"""
    DevId: Annotated[str, Field(description="设备ID")]
    Id: Annotated[int, Field(description="记录ID")]
    Ch: Annotated[int, Field(description="通道号")]
    BeginTime: Annotated[int, Field(description="开始时间戳")]
    EndTime: Annotated[int, Field(description="结束时间戳")]
    TimeLen: Annotated[int, Field(description="通话时长(秒)")]
    Type: Annotated[CallType, Field(description="通话类型")]
    Phone: Annotated[str, Field(description="电话号码")]
    DtmfKeys: Annotated[str, Field(default="", description="DTMF按键")]
    RingCount: Annotated[int, Field(default=0, description="振铃次数")]
    FileSize: Annotated[int, Field(description="文件大小(字节)")]
    FileName: Annotated[str, Field(description="文件路径")]
    CustomId: Annotated[str, Field(default="", description="自定义ID")]
    uuid: Annotated[str, Field(description="记录UUID")]
    UploadState: Annotated[int, Field(description="上传状态")]

class CallRecordUploadRequest(BaseModel):
    """通话录音上传请求"""
    record: Annotated[CallRecord, Field(description="通话记录")]
    fileName: Annotated[str | None, Field(default=None, description="文件名称")]
    HasFile: Annotated[int, Field(description="是否包含文件(1/0)")]
    file: Annotated[UploadFile | None, Field(default=None, description="录音文件")]

    model_config = ConfigDict(arbitrary_types_allowed=True)

class CallSystemResponse(BaseModel):
    """CallSystem接口响应"""
    Code: Annotated[int, Field(description="响应状态码，0表示成功，-1表示失败")]
    errMsg: Annotated[str, Field(description="错误信息")]
    NextUploadId: Annotated[int | None, Field(default=None, description="下一个上传ID")]
