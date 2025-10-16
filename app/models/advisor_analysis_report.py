"""顾问分析报告数据模型"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Boolean
from sqlalchemy.sql import func
from app.db.database import Base


class AdvisorAnalysisReport(Base):
    """顾问分析报告表"""
    
    __tablename__ = "advisor_analysis_reports"
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    advisor_id = Column(Integer, nullable=False, comment="顾问ID")
    advisor_name = Column(String(100), nullable=False, comment="顾问姓名")
    report_date = Column(Date, nullable=False, comment="报告日期")
    report_type = Column(String(50), default="daily", comment="报告类型")
    
    # 文件信息
    local_file_path = Column(String(500), comment="本地文件路径")
    cloud_url = Column(String(1000), comment="云存储URL")
    cloud_object_key = Column(String(500), comment="云存储对象键")
    
    # 报告内容
    report_content = Column(Text, comment="报告内容（Markdown格式）")
    report_summary = Column(Text, comment="报告摘要")
    
    # 统计信息
    total_calls = Column(Integer, default=0, comment="总通话数")
    connected_calls = Column(Integer, default=0, comment="接通数")
    connection_rate = Column(String(20), comment="接通率")
    effective_calls = Column(Integer, default=0, comment="有效通话数")
    effective_call_rate = Column(String(20), comment="有效通话率")
    total_duration_minutes = Column(String(20), comment="总通话时长（分钟）")
    
    # 状态信息
    is_uploaded = Column(Boolean, default=False, comment="是否已上传到云存储")
    is_deleted = Column(Boolean, default=False, comment="本地文件是否已删除")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<AdvisorAnalysisReport(id={self.id}, advisor_id={self.advisor_id}, report_date={self.report_date})>"
