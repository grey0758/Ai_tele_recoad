"""
定时任务相关模型定义

基于 scheduled_tasks 和 task_execution_logs 表的 SQLAlchemy 模型定义
"""

from datetime import datetime, time
from typing import Optional
from sqlalchemy import Integer, String, Text, Boolean, DateTime, Time, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class ScheduledTasks(Base):
    """定时任务配置表模型"""

    __tablename__ = "scheduled_tasks"

    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    task_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="任务名称"
    )
    task_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="任务类型"
    )
    cron_expression: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Cron表达式"
    )
    start_time: Mapped[Optional[time]] = mapped_column(Time, comment="开始时间")
    end_time: Mapped[Optional[time]] = mapped_column(Time, comment="结束时间")
    interval_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, comment="间隔分钟数"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="任务描述")
    last_run: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="上次执行时间"
    )
    next_run: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="下次执行时间"
    )

    # 时间字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 关联关系
    execution_logs: Mapped[list["TaskExecutionLogs"]] = relationship(
        "TaskExecutionLogs", back_populates="task"
    )


class TaskExecutionLogs(Base):
    """任务执行日志表模型"""

    __tablename__ = "task_execution_logs"

    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scheduled_tasks.id"), comment="任务ID"
    )
    advisor_id: Mapped[Optional[int]] = mapped_column(Integer, comment="顾问ID")
    execution_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="执行时间"
    )
    status: Mapped[str] = mapped_column(
        Enum("success", "failed", "running", name="task_status"),
        default="running",
        comment="执行状态",
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, comment="错误信息")
    execution_duration: Mapped[Optional[int]] = mapped_column(
        Integer, comment="执行时长(秒)"
    )

    # 时间字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )

    # 关联关系
    task: Mapped["ScheduledTasks"] = relationship(
        "ScheduledTasks", back_populates="execution_logs"
    )
