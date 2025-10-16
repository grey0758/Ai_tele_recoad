"""顾问分析报告 Pydantic 模式"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class AdvisorAnalysisReportBase(BaseModel):
    """顾问分析报告基础模式"""
    
    advisor_id: int = Field(description="顾问ID")
    advisor_name: str = Field(description="顾问姓名")
    report_date: date = Field(description="报告日期")
    report_type: str = Field(default="daily", description="报告类型")
    
    # 文件信息
    local_file_path: Optional[str] = Field(default=None, description="本地文件路径")
    cloud_url: Optional[str] = Field(default=None, description="云存储URL")
    cloud_object_key: Optional[str] = Field(default=None, description="云存储对象键")
    
    # 报告内容
    report_content: Optional[str] = Field(default=None, description="报告内容（Markdown格式）")
    report_summary: Optional[str] = Field(default=None, description="报告摘要")
    
    # 统计信息
    total_calls: int = Field(default=0, description="总通话数")
    connected_calls: int = Field(default=0, description="接通数")
    connection_rate: Optional[str] = Field(default=None, description="接通率")
    effective_calls: int = Field(default=0, description="有效通话数")
    effective_call_rate: Optional[str] = Field(default=None, description="有效通话率")
    total_duration_minutes: Optional[str] = Field(default=None, description="总通话时长（分钟）")
    
    # 状态信息
    is_uploaded: bool = Field(default=False, description="是否已上传到云存储")
    is_deleted: bool = Field(default=False, description="本地文件是否已删除")


class AdvisorAnalysisReportCreate(AdvisorAnalysisReportBase):
    """创建顾问分析报告模式"""

class AdvisorAnalysisReportUpdate(BaseModel):
    """更新顾问分析报告模式"""
    
    cloud_url: Optional[str] = Field(default=None, description="云存储URL")
    cloud_object_key: Optional[str] = Field(default=None, description="云存储对象键")
    is_uploaded: Optional[bool] = Field(default=None, description="是否已上传到云存储")
    is_deleted: Optional[bool] = Field(default=None, description="本地文件是否已删除")


class AdvisorAnalysisReportResponse(AdvisorAnalysisReportBase):
    """顾问分析报告响应模式"""
    
    id: int = Field(description="主键ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    model_config = {"from_attributes": True}
