# app/models/call_record.py
"""电话记录数据类"""
import uuid
from typing import List, Annotated
from datetime import datetime
from pydantic import BaseModel, Field


class DialogEntry(BaseModel):
    """对话记录数据类"""
    speaker: Annotated[str, Field(description="说话人标识")]
    content: Annotated[str, Field(description="对话内容")]
    timestamp: Annotated[datetime, Field(default_factory=datetime.now, description="对话时间戳")]

class DialogRecord(BaseModel):
    """对话记录数据类"""
    call_id: Annotated[str, Field(description="通话唯一标识")]
    dialog_record: Annotated[List[DialogEntry], Field(default_factory=list, description="对话记录列表")]

class CallRecord(BaseModel):
    """电话记录数据类"""
    call_id: Annotated[str, Field(default_factory=lambda: str(uuid.uuid4()), description="通话唯一标识")]
    phone_number: Annotated[str | None, Field(default=None, description="电话号码")]
    tts_opening: Annotated[str | None, Field(default=None, description="TTS开场白")]
    custom_id: Annotated[str | None, Field(default=None, description="自定义标识")]
    call_type: Annotated[str | None, Field(default=None, description="通话类型")]
    status: Annotated[str | None, Field(default=None, description="通话状态")]
    updated_at: Annotated[datetime, Field(default_factory=datetime.now, description="更新时间")]
    start_time: Annotated[datetime | None, Field(default=None, description="通话开始时间")]
    end_time: Annotated[datetime | None, Field(default=None, description="通话结束时间")]
    duration: Annotated[int, Field(default=0,description="通话时长（秒）")]
    instance: Annotated[int, Field(description="设备实例ID")]
    dialog_record: Annotated[List[DialogEntry], Field(default_factory=list, description="对话记录列表")]
    notes: Annotated[str | None, Field(default=None, description="备注信息")]
