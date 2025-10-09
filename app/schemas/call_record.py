"""
通话记录相关的Pydantic模式定义

提供通话记录的请求、响应和查询模式
"""
from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CallTypeEnum(str, Enum):
    """通话类型枚举"""

    CALL_IN = "callIn"
    CALL_OUT = "callOut"
    CALL_IN_NO_ANSWER = "callInNoAnswer"
    CALL_OUT_NO_ANSWER = "callOutNoAnswer"


class CallRecordCreate(BaseModel):
    """创建通话记录请求"""

    dev_id: str = Field(max_length=200, description="设备ID")
    record_id: int = Field(description="记录ID")
    ch: int = Field(description="通道号")
    begin_time: int = Field(description="开始时间戳")
    end_time: int = Field(description="结束时间戳")
    time_len: int = Field(description="通话时长(秒)")
    call_type: CallTypeEnum = Field(description="通话类型")
    phone: str = Field(description="电话号码")
    dtmf_keys: str = Field(default="", description="DTMF按键")
    ring_count: int = Field(default=0, description="振铃次数")
    file_size: int = Field(description="文件大小(字节)")
    file_name: str = Field(description="文件路径")
    custom_id: str = Field(default="", description="自定义ID")
    record_uuid: str = Field(description="记录UUID")
    upload_state: int = Field(description="上传状态")

    # 存储信息
    local_path: Optional[str] = Field(default=None, description="本地文件路径")
    cloud_url: Optional[str] = Field(default=None, description="云存储URL")
    cloud_uploaded: bool = Field(default=False, description="是否已上传到云存储")

    # 业务扩展字段
    call_no: Optional[str] = Field(default=None, description="通话编号")
    lead_id: Optional[int] = Field(default=None, description="关联的线索ID")
    advisor_id: Optional[int] = Field(default=None, description="通话顾问ID")
    advisor_group_id: Optional[int] = Field(default=None, description="所属顾问组ID")
    advisor_group_sub_id: Optional[int] = Field(
        default=None, description="所属顾问组子ID"
    )
    conversation_content: Optional[dict] = Field(
        default=None, description="对话记录JSON"
    )
    call_summary: Optional[str] = Field(default=None, description="通话总结")
    call_quality_score: Optional[int] = Field(default=None, description="通话质量评分")
    quality_notes: Optional[str] = Field(default=None, description="质检备注")


class CallRecordUpdate(BaseModel):
    """更新通话记录请求"""

    dev_id: Optional[str] = Field(default=None, max_length=200, description="设备ID")
    record_id: Optional[int] = Field(default=None, description="记录ID")
    ch: Optional[int] = Field(default=None, description="通道号")
    begin_time: Optional[int] = Field(default=None, description="开始时间戳")
    end_time: Optional[int] = Field(default=None, description="结束时间戳")
    time_len: Optional[int] = Field(default=None, description="通话时长(秒)")
    call_type: Optional[CallTypeEnum] = Field(default=None, description="通话类型")
    phone: Optional[str] = Field(default=None, description="电话号码")
    dtmf_keys: Optional[str] = Field(default=None, description="DTMF按键")
    ring_count: Optional[int] = Field(default=None, description="振铃次数")
    file_size: Optional[int] = Field(default=None, description="文件大小(字节)")
    file_name: Optional[str] = Field(default=None, description="文件路径")
    custom_id: Optional[str] = Field(default=None, description="自定义ID")
    upload_state: Optional[int] = Field(default=None, description="上传状态")

    # 存储信息
    local_path: Optional[str] = Field(default=None, description="本地文件路径")
    cloud_url: Optional[str] = Field(default=None, description="云存储URL")
    cloud_uploaded: Optional[bool] = Field(
        default=None, description="是否已上传到云存储"
    )

    # 业务扩展字段
    call_no: Optional[str] = Field(default=None, description="通话编号")
    lead_id: Optional[int] = Field(default=None, description="关联的线索ID")
    advisor_id: Optional[int] = Field(default=None, description="通话顾问ID")
    advisor_group_id: Optional[int] = Field(default=None, description="所属顾问组ID")
    advisor_group_sub_id: Optional[int] = Field(
        default=None, description="所属顾问组子ID"
    )
    conversation_content: Optional[dict] = Field(
        default=None, description="对话记录JSON"
    )
    call_summary: Optional[str] = Field(default=None, description="通话总结")
    call_quality_score: Optional[int] = Field(default=None, description="通话质量评分")
    quality_notes: Optional[str] = Field(default=None, description="质检备注")


class CallRecordResponse(BaseModel):
    """通话记录响应"""

    id: int = Field(description="主键ID")
    dev_id: str = Field(max_length=200, description="设备ID")
    record_id: int = Field(description="记录ID")
    ch: int = Field(description="通道号")
    begin_time: int = Field(description="开始时间戳")
    end_time: int = Field(description="结束时间戳")
    time_len: int = Field(description="通话时长(秒)")
    call_type: CallTypeEnum = Field(description="通话类型")
    phone: str = Field(description="电话号码")
    dtmf_keys: str = Field(description="DTMF按键")
    ring_count: int = Field(description="振铃次数")
    file_size: int = Field(description="文件大小(字节)")
    file_name: str = Field(description="文件路径")
    custom_id: str = Field(description="自定义ID")
    record_uuid: str = Field(description="记录UUID")
    upload_state: int = Field(description="上传状态")

    # 存储信息
    local_path: Optional[str] = Field(description="本地文件路径")
    cloud_url: Optional[str] = Field(description="云存储URL")
    cloud_uploaded: bool = Field(description="是否已上传到云存储")

    # 业务扩展字段
    call_no: Optional[str] = Field(description="通话编号")
    lead_id: Optional[int] = Field(description="关联的线索ID")
    advisor_id: Optional[int] = Field(description="通话顾问ID")
    advisor_group_id: Optional[int] = Field(description="所属顾问组ID")
    advisor_group_sub_id: Optional[int] = Field(description="所属顾问组子ID")
    conversation_content: Optional[dict] = Field(description="对话记录JSON")
    call_summary: Optional[str] = Field(description="通话总结")
    call_quality_score: Optional[int] = Field(description="通话质量评分")
    quality_notes: Optional[str] = Field(description="质检备注")

    # 时间戳
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class CallRecordQueryParams(BaseModel):
    """通话记录查询参数"""

    # 分页参数
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")
    sort_field: str = Field(default="created_at", description="排序字段")
    sort_order: str = Field(default="desc", description="排序方向")

    # 基础查询条件
    dev_id: Optional[str] = Field(default=None, max_length=200, description="设备ID")
    record_id: Optional[int] = Field(default=None, description="记录ID")
    phone: Optional[str] = Field(default=None, description="电话号码")
    call_type: Optional[CallTypeEnum] = Field(default=None, description="通话类型")
    upload_state: Optional[int] = Field(default=None, description="上传状态")
    cloud_uploaded: Optional[bool] = Field(
        default=None, description="是否已上传到云存储"
    )

    # 业务查询条件
    lead_id: Optional[int] = Field(default=None, description="关联的线索ID")
    advisor_id: Optional[int] = Field(default=None, description="通话顾问ID")
    advisor_group_id: Optional[int] = Field(default=None, description="所属顾问组ID")

    # 时间范围查询
    begin_time_start: Optional[int] = Field(default=None, description="开始时间戳起始")
    begin_time_end: Optional[int] = Field(default=None, description="开始时间戳结束")
    created_at_start: Optional[datetime] = Field(
        default=None, description="创建时间起始"
    )
    created_at_end: Optional[datetime] = Field(default=None, description="创建时间结束")

    # 搜索关键词
    search: Optional[str] = Field(default=None, description="搜索关键词")


class CallRecordListResponse(BaseModel):
    """通话记录列表响应"""

    items: List[CallRecordResponse] = Field(description="通话记录列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页数量")
    pages: int = Field(description="总页数")
