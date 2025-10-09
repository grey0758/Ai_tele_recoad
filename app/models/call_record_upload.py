"""
通话记录上传模型定义

基于 call_records 表的 SQLAlchemy 模型定义
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, DateTime, SmallInteger, Integer, Boolean, Text, JSON, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class CallRecordUpload(Base):
    """通话记录上传表模型"""

    __tablename__ = "call_records"

    # 主键
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID，使用BIGINT支持大数据量")

    # CallRecordUploadRequest 主要字段
    dev_id: Mapped[str] = mapped_column(String(50), nullable=False, comment="设备ID")
    record_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="记录ID")
    ch: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="通道号")
    begin_time: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="开始时间戳")
    end_time: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="结束时间戳")
    time_len: Mapped[int] = mapped_column(Integer, nullable=False, comment="通话时长(秒)")
    call_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="通话类型")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, comment="电话号码")
    dtmf_keys: Mapped[str] = mapped_column(String(100), default="", comment="DTMF按键")
    ring_count: Mapped[int] = mapped_column(Integer, default=0, comment="振铃次数")
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="文件大小(字节)")
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件路径")
    custom_id: Mapped[str] = mapped_column(String(100), default="", comment="自定义ID")
    record_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, comment="记录UUID")
    upload_state: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="上传状态")

    # 存储信息
    local_path: Mapped[Optional[str]] = mapped_column(String(500), comment="本地文件路径")
    cloud_url: Mapped[Optional[str]] = mapped_column(String(500), comment="云存储URL")
    cloud_uploaded: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已上传到云存储")

    # 业务扩展字段
    call_no: Mapped[Optional[str]] = mapped_column(String(30), unique=True, comment="通话编号：业务唯一标识，格式如CALL20240917001")
    lead_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="关联的线索ID")
    advisor_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="通话顾问ID")
    advisor_group_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="所属顾问组ID")
    advisor_group_sub_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="所属顾问组子ID")
    conversation_content: Mapped[Optional[dict]] = mapped_column(JSON, comment="对话记录：包含对话内容、关键信息提取、客户需求等")
    call_summary: Mapped[Optional[str]] = mapped_column(Text, comment="通话总结：顾问填写的通话要点和后续跟进计划")
    call_quality_score: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="通话质量评分：1-100分，用于质检评估")
    quality_notes: Mapped[Optional[str]] = mapped_column(Text, comment="质检备注：质检人员的评价和建议")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间") # pylint: disable=not-callable
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="更新时间") # pylint: disable=not-callable

    # 性能优化索引
    __table_args__ = (
        Index("idx_dev_id", "dev_id"),
        Index("idx_record_id", "record_id"),
        Index("idx_phone", "phone"),
        Index("idx_call_type", "call_type"),
        Index("idx_begin_time", "begin_time"),
        Index("idx_upload_state", "upload_state"),
        Index("idx_cloud_uploaded", "cloud_uploaded"),
        Index("idx_lead_id", "lead_id"),
        Index("idx_advisor_id", "advisor_id"),
        Index("idx_advisor_group", "advisor_group_id"),
        Index("idx_call_type_time", "call_type", "begin_time"),
        Index("idx_phone_time", "phone", "begin_time"),
        Index("idx_dev_record", "dev_id", "record_id", unique=True),
    )
