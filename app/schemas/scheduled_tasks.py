"""
定时任务相关Schema定义

定义定时任务和任务执行日志的Pydantic模型
"""

from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.base import ResponseData


class ScheduledTaskBase(BaseModel):
    """定时任务基础模型"""
    task_name: str = Field(..., description="任务名称", max_length=100)
    task_type: str = Field(..., description="任务类型", max_length=50)
    cron_expression: str = Field(..., description="Cron表达式", max_length=100)
    start_time: Optional[time] = Field(None, description="开始时间")
    end_time: Optional[time] = Field(None, description="结束时间")
    interval_minutes: Optional[int] = Field(None, description="间隔分钟数")
    is_active: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="任务描述")


class ScheduledTaskCreate(ScheduledTaskBase):
    """创建定时任务模型"""
    pass


class ScheduledTaskUpdate(BaseModel):
    """更新定时任务模型"""
    task_name: Optional[str] = Field(None, description="任务名称", max_length=100)
    task_type: Optional[str] = Field(None, description="任务类型", max_length=50)
    cron_expression: Optional[str] = Field(None, description="Cron表达式", max_length=100)
    start_time: Optional[time] = Field(None, description="开始时间")
    end_time: Optional[time] = Field(None, description="结束时间")
    interval_minutes: Optional[int] = Field(None, description="间隔分钟数")
    is_active: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="任务描述")


class ScheduledTaskResponse(ScheduledTaskBase):
    """定时任务响应模型"""
    id: int = Field(..., description="主键ID")
    last_run: Optional[datetime] = Field(None, description="上次执行时间")
    next_run: Optional[datetime] = Field(None, description="下次执行时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class TaskExecutionLogBase(BaseModel):
    """任务执行日志基础模型"""
    task_id: int = Field(..., description="任务ID")
    advisor_id: Optional[int] = Field(None, description="顾问ID")
    execution_time: Optional[datetime] = Field(None, description="执行时间")
    status: str = Field(..., description="执行状态", pattern="^(success|failed|running)$")
    error_message: Optional[str] = Field(None, description="错误信息")
    execution_duration: Optional[int] = Field(None, description="执行时长(秒)")


class TaskExecutionLogCreate(TaskExecutionLogBase):
    """创建任务执行日志模型"""
    pass


class TaskExecutionLogResponse(TaskExecutionLogBase):
    """任务执行日志响应模型"""
    id: int = Field(..., description="主键ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class TaskExecutionLogWithTask(TaskExecutionLogResponse):
    """包含任务信息的执行日志响应模型"""
    task: Optional[ScheduledTaskResponse] = Field(None, description="关联的任务信息")


# 响应类型定义
ScheduledTaskListResponse = ResponseData[List[ScheduledTaskResponse]]
ScheduledTaskDetailResponse = ResponseData[ScheduledTaskResponse]
TaskExecutionLogListResponse = ResponseData[List[TaskExecutionLogResponse]]
TaskExecutionLogDetailResponse = ResponseData[TaskExecutionLogResponse]
TaskExecutionLogCreateResponse = ResponseData[TaskExecutionLogResponse]
