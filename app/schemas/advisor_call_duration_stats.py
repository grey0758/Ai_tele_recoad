"""
顾问通话时长统计相关的 Pydantic Schema 定义

用于 API 请求和响应的数据验证和序列化
"""

from datetime import datetime, date
from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict


class AdvisorCallDurationStatsBase(BaseModel):
    """顾问通话时长统计基础 Schema"""
    advisor_id: Annotated[Optional[int], Field(default=None, description="顾问ID")]    
    advisor_name: Annotated[Optional[str], Field(default=None, description="顾问姓名")]
    stats_date: Annotated[date, Field(..., description="统计日期")]
    device_id: Annotated[str, Field(..., max_length=50, description="设备ID")]

    # 总体统计
    total_calls: Annotated[int, Field(default=0, description="总呼叫记录数")]
    total_connected: Annotated[int, Field(default=0, description="总接通数目")]
    total_unconnected: Annotated[int, Field(default=0, description="未接通总数")]
    total_duration: Annotated[int, Field(default=0, description="总通话时长(秒)")]
    connection_rate: Annotated[float, Field(default=0.00, description="接通率(%)")]
    
    # 呼出统计
    outbound_calls: Annotated[int, Field(default=0, description="总呼出记录")]
    outbound_connected: Annotated[int, Field(default=0, description="呼出接通数目")]
    outbound_unconnected: Annotated[int, Field(default=0, description="呼出未接通数")]
    outbound_duration: Annotated[int, Field(default=0, description="呼出总通话时长(秒)")]
    outbound_connection_rate: Annotated[float, Field(default=0.00, description="呼出接通率(%)")]
    
    # 呼入统计
    inbound_calls: Annotated[int, Field(default=0, description="总呼入记录")]
    inbound_connected: Annotated[int, Field(default=0, description="呼入接通数目")]
    inbound_unconnected: Annotated[int, Field(default=0, description="呼入未接通数")]
    inbound_duration: Annotated[int, Field(default=0, description="呼入总通话时长(秒)")]
    inbound_connection_rate: Annotated[float, Field(default=0.00, description="呼入接通率(%)")]
    
    # 通话时长分段统计(总体) - 修正字段名匹配API
    duration_under_5s: Annotated[int, Field(default=0, description="通话时长<5秒总数")]
    duration_5s_to_10s: Annotated[int, Field(default=0, description="通话时长5-10秒总数")]
    duration_10s_to_20s: Annotated[int, Field(default=0, description="通话时长10-20秒总数")]
    duration_20s_to_30s: Annotated[int, Field(default=0, description="通话时长20-30秒总数")]
    duration_30s_to_45s: Annotated[int, Field(default=0, description="通话时长30-45秒总数")]
    duration_45s_to_60s: Annotated[int, Field(default=0, description="通话时长45-60秒总数")]
    duration_over_60s: Annotated[int, Field(default=0, description="通话时长大于60秒总数")]
    
    # 呼出通话时长分段统计 - 修正字段名匹配API
    outbound_duration_under_5s: Annotated[int, Field(default=0, description="呼出通话时长<5秒")]
    outbound_duration_5s_to_10s: Annotated[int, Field(default=0, description="呼出通话时长5-10秒")]
    outbound_duration_10s_to_20s: Annotated[int, Field(default=0, description="呼出通话时长10-20秒")]
    outbound_duration_20s_to_30s: Annotated[int, Field(default=0, description="呼出通话时长20-30秒")]
    outbound_duration_30s_to_45s: Annotated[int, Field(default=0, description="呼出通话时长30-45秒")]
    outbound_duration_45s_to_60s: Annotated[int, Field(default=0, description="呼出通话时长45-60秒")]
    outbound_duration_over_60s: Annotated[int, Field(default=0, description="呼出通话时长大于60秒")]
    
    # 呼入通话时长分段统计 - 修正字段名匹配API
    inbound_duration_under_5s: Annotated[int, Field(default=0, description="呼入通话时长<5秒")]
    inbound_duration_5s_to_10s: Annotated[int, Field(default=0, description="呼入通话时长5-10秒")]
    inbound_duration_10s_to_20s: Annotated[int, Field(default=0, description="呼入通话时长10-20秒")]
    inbound_duration_20s_to_30s: Annotated[int, Field(default=0, description="呼入通话时长20-30秒")]
    inbound_duration_30s_to_45s: Annotated[int, Field(default=0, description="呼入通话时长30-45秒")]
    inbound_duration_45s_to_60s: Annotated[int, Field(default=0, description="呼入通话时长45-60秒")]
    inbound_duration_over_60s: Annotated[int, Field(default=0, description="呼入通话时长大于60秒")]

class AdvisorCallDurationStatsResponse(AdvisorCallDurationStatsBase):
    """顾问通话时长统计响应 Schema"""
    id : Annotated[int, Field(default=None, description="主键ID")]
    created_at: datetime = Field(default=None, description="创建时间")
    updated_at: datetime = Field(default=None, description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)


class AdvisorCallDurationStatsUpsertRequest(AdvisorCallDurationStatsBase):
    """顾问通话时长统计更新或插入请求 Schema"""
    pass

