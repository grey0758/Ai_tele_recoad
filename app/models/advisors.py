"""
顾问模型定义

基于 advisors 表的 SQLAlchemy 模型定义
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import SmallInteger, String, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Advisors(Base):
    """顾问表模型"""

    __tablename__ = "advisors"

    # 主键
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, comment="主键ID")
    group_id: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="所属组ID")
    sub_group_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="所属子组ID：支持顾问分配到子组")
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="顾问姓名")
    status: Mapped[int] = mapped_column(SmallInteger, default=1, comment="状态：1=在职，0=离职，2=休假")

    # 时间字段
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间") # pylint: disable=not-callable
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="更新时间") # pylint: disable=not-callable

    # 索引设计
    __table_args__ = (
        Index("idx_group_status", "group_id", "status"),
        Index("idx_sub_group_status", "sub_group_id", "status"),
        Index("idx_status", "status"),
    )
