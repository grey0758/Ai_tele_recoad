"""
顾问通话时长统计模型定义

基于 advisor_call_duration_stats 表的 SQLAlchemy 模型定义
"""

from datetime import datetime, date
from sqlalchemy import BigInteger, String, Date, SmallInteger, Index, UniqueConstraint
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class AdvisorCallDurationStats(Base):
    """顾问通话时长统计表模型"""
    __tablename__ = "advisor_call_duration_stats"

    # 主键
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    advisor_id: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="顾问ID")
    advisor_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="顾问姓名")
    stats_date: Mapped[date] = mapped_column(Date, nullable=False, comment="统计日期")
    device_id: Mapped[str] = mapped_column(String(50), nullable=False, comment="设备ID")
    
    # 总体统计
    total_calls: Mapped[int] = mapped_column(BigInteger, default=0, comment="总呼叫记录数")
    total_connected: Mapped[int] = mapped_column(BigInteger, default=0, comment="总接通数目")
    total_unconnected: Mapped[int] = mapped_column(BigInteger, default=0, comment="未接通总数")
    total_duration: Mapped[int] = mapped_column(BigInteger, default=0, comment="总通话时长(秒)")
    total_duration_correction: Mapped[int] = mapped_column(BigInteger, default=0, comment="总通话时长修正值(秒)")
    connection_rate: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.00, comment="接通率(%)")
    
    # 呼出统计
    outbound_calls: Mapped[int] = mapped_column(BigInteger, default=0, comment="总呼出记录")
    outbound_connected: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼出接通数目")
    outbound_unconnected: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼出未接通数")
    outbound_duration: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼出总通话时长(秒)")
    outbound_connection_rate: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.00, comment="呼出接通率(%)")
    
    # 呼入统计
    inbound_calls: Mapped[int] = mapped_column(BigInteger, default=0, comment="总呼入记录")
    inbound_connected: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼入接通数目")
    inbound_unconnected: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼入未接通数")
    inbound_duration: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼入总通话时长(秒)")
    inbound_connection_rate: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.00, comment="呼入接通率(%)")
    
    # 通话时长分段统计(总体) - 修正字段名匹配API
    duration_under_5s: Mapped[int] = mapped_column(BigInteger, default=0, comment="通话时长<5秒总数")
    duration_5s_to_10s: Mapped[int] = mapped_column(BigInteger, default=0, comment="通话时长5-10秒总数")
    duration_10s_to_20s: Mapped[int] = mapped_column(BigInteger, default=0, comment="通话时长10-20秒总数")
    duration_20s_to_30s: Mapped[int] = mapped_column(BigInteger, default=0, comment="通话时长20-30秒总数")
    duration_30s_to_45s: Mapped[int] = mapped_column(BigInteger, default=0, comment="通话时长30-45秒总数")
    duration_45s_to_60s: Mapped[int] = mapped_column(BigInteger, default=0, comment="通话时长45-60秒总数")
    duration_over_60s: Mapped[int] = mapped_column(BigInteger, default=0, comment="通话时长大于60秒总数")
    
    # 呼出通话时长分段统计 - 修正字段名匹配API
    outbound_duration_under_5s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼出通话时长<5秒")
    outbound_duration_5s_to_10s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼出通话时长5-10秒")
    outbound_duration_10s_to_20s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼出通话时长10-20秒")
    outbound_duration_20s_to_30s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼出通话时长20-30秒")
    outbound_duration_30s_to_45s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼出通话时长30-45秒")
    outbound_duration_45s_to_60s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼出通话时长45-60秒")
    outbound_duration_over_60s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼出通话时长大于60秒")
    
    # 呼入通话时长分段统计 - 修正字段名匹配API
    inbound_duration_under_5s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼入通话时长<5秒")
    inbound_duration_5s_to_10s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼入通话时长5-10秒")
    inbound_duration_10s_to_20s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼入通话时长10-20秒")
    inbound_duration_20s_to_30s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼入通话时长20-30秒")
    inbound_duration_30s_to_45s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼入通话时长30-45秒")
    inbound_duration_45s_to_60s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼入通话时长45-60秒")
    inbound_duration_over_60s: Mapped[int] = mapped_column(BigInteger, default=0, comment="呼入通话时长大于60秒")
    
    # 时间字段
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 唯一约束和索引
    __table_args__ = (
        UniqueConstraint('advisor_id', 'stats_date', name='uk_advisor_date'),
        Index('idx_advisor_id', 'advisor_id'),
        Index('idx_stats_date', 'stats_date')
    )


class AdvisorDeviceConfig(Base):
    """顾问设备配置表模型"""
    __tablename__ = "advisor_device_config"

    # 主键
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID")
    device_id: Mapped[str] = mapped_column(String(50), nullable=False, comment="设备ID")
    advisor_id: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="顾问ID")
    advisor_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="顾问姓名")
    
    # 时间字段
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 唯一约束和索引
    __table_args__ = (
        UniqueConstraint('device_id', name='uk_device_id'),
        Index('idx_device_id', 'device_id')
    )