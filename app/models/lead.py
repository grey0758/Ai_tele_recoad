"""
线索模型定义

基于 lead2_leads 表的 SQLAlchemy 模型定义
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, DateTime, SmallInteger, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Lead(Base):
    """线索主表模型"""

    __tablename__ = "leads"

    # 主键
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="主键ID，使用BIGINT支持大数据量")

    # 核心分类信息
    category_id: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="线索类型ID：关联lead_categories表")
    sub_category_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="子类型ID：关联lead_categories表的二级分类")

    # 分配信息
    advisor_group_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="分配的顾问组ID")
    advisor_group_sub_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="分配的顾问组子ID")
    advisor_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="分配的顾问ID")

    # 客户基础信息
    customer_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="客户ID")
    customer_name: Mapped[Optional[str]] = mapped_column(String(50), comment="客户姓名")
    customer_phone: Mapped[Optional[str]] = mapped_column(String(20), comment="客户电话：主要联系方式")
    customer_email: Mapped[Optional[str]] = mapped_column(String(100), comment="客户邮箱")
    customer_wechat_name: Mapped[Optional[str]] = mapped_column(String(50), comment="客户微信昵称")
    customer_wechat_number: Mapped[Optional[str]] = mapped_column(String(50), comment="客户微信号码")

    # 状态字段（主状态+子状态设计）
    call_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="电话主状态ID：关联call_status表")
    call_sub_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="电话子状态ID：关联call_status表的二级分类")

    wechat_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="微信主状态ID：关联wechat_status表")
    wechat_sub_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="微信子状态ID：关联wechat_status表的二级分类")

    # 两个独立的私域状态
    private_domain_review_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="私域回看主状态ID：关联private_domain_review_status表")
    private_domain_review_sub_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="私域回看子状态ID：关联private_domain_review_status表的二级分类")

    private_domain_participation_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="私域参加主状态ID：关联private_domain_participation_status表")
    private_domain_participation_sub_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="私域参加子状态ID：关联private_domain_participation_status表的二级分类")

    schedule_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="日程主状态ID：关联schedule_status表")
    schedule_sub_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="日程子状态ID：关联schedule_status表的二级分类")
    schedule_times: Mapped[int] = mapped_column(SmallInteger, default=0, comment="日程次数")

    contract_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="合同主状态ID：关联contract_status表")
    contract_sub_status_id: Mapped[Optional[int]] = mapped_column(SmallInteger, comment="合同子状态ID：关联contract_status表的二级分类")

    # 分析字段
    analysis_failed_records: Mapped[int] = mapped_column(SmallInteger, default=0, comment="未能联系次数")
    last_contact_record_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="最后一次可联系通话ID")
    last_contact_time: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="最后一次可联系时间")
    last_analysis_failed_record_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="最后一次未能联系通话ID")
    last_analysis_failed_time: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="最后一次未能联系时间")

    # 时间字段
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间") # pylint: disable=not-callable
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="更新时间") # pylint: disable=not-callable

    # 性能优化索引
    __table_args__ = (
        Index("idx_category_advisor", "category_id", "advisor_id"),
        Index("idx_advisor_status", "advisor_id", "call_status_id"),
        Index("idx_phone", "customer_phone"),
        Index("idx_created_category", "created_at", "category_id"),
        Index("idx_status_combination", "call_status_id", "wechat_status_id", "schedule_status_id"),
    )
