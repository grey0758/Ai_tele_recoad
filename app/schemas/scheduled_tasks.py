"""
定时任务相关Schema定义

定义定时任务和任务执行日志的Pydantic模型
"""

from datetime import datetime, time
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.base import ResponseData


class ScheduledTaskBase(BaseModel):
    """定时任务基础模型"""
    task_name: Annotated[str, Field(..., description="任务名称", max_length=100)]
    task_type: Annotated[str, Field(..., description="任务类型", max_length=50)]
    cron_expression: Annotated[str, Field(..., description="Cron表达式", max_length=100)]
    start_time: Annotated[Optional[time], Field(None, description="开始时间")]
    end_time: Annotated[Optional[time], Field(None, description="结束时间")]
    interval_minutes: Annotated[Optional[int], Field(None, description="间隔分钟数")]
    is_active: Annotated[bool, Field(True, description="是否启用")]
    description: Annotated[Optional[str], Field(None, description="任务描述")]


class ScheduledTaskCreate(ScheduledTaskBase):
    """创建定时任务模型"""

class ScheduledTaskUpdate(BaseModel):
    """更新定时任务模型"""
    task_name: Annotated[Optional[str], Field(None, description="任务名称", max_length=100)]
    task_type: Annotated[Optional[str], Field(None, description="任务类型", max_length=50)]
    cron_expression: Annotated[Optional[str], Field(None, description="Cron表达式", max_length=100)]
    start_time: Annotated[Optional[time], Field(None, description="开始时间")]
    end_time: Annotated[Optional[time], Field(None, description="结束时间")]
    interval_minutes: Annotated[Optional[int], Field(None, description="间隔分钟数")]
    is_active: Annotated[Optional[bool], Field(None, description="是否启用")]
    description: Annotated[Optional[str], Field(None, description="任务描述")]


class ScheduledTaskResponse(ScheduledTaskBase):
    """定时任务响应模型"""
    id: Annotated[int, Field(..., description="主键ID")]
    last_run: Annotated[Optional[datetime], Field(None, description="上次执行时间")]
    next_run: Annotated[Optional[datetime], Field(None, description="下次执行时间")]
    created_at: Annotated[datetime, Field(..., description="创建时间")]
    updated_at: Annotated[datetime, Field(..., description="更新时间")]

    model_config = ConfigDict(from_attributes=True)


class TaskExecutionLogBase(BaseModel):
    """任务执行日志基础模型"""
    task_id: Annotated[int, Field(..., description="任务ID")]
    advisor_id: Annotated[Optional[int], Field(None, description="顾问ID")]
    execution_time: Annotated[Optional[datetime], Field(None, description="执行时间")]
    status: Annotated[str, Field(..., description="执行状态", pattern="^(success|failed|running)$")]
    error_message: Annotated[Optional[str], Field(None, description="错误信息")]
    execution_duration: Annotated[Optional[int], Field(None, description="执行时长(秒)")]


class TaskExecutionLogCreate(TaskExecutionLogBase):
    """创建任务执行日志模型"""

class TaskExecutionLogResponse(TaskExecutionLogBase):
    """任务执行日志响应模型"""
    id: Annotated[int, Field(..., description="主键ID")]
    created_at: Annotated[datetime, Field(..., description="创建时间")]

    model_config = ConfigDict(from_attributes=True)


class TaskExecutionLogWithTask(TaskExecutionLogResponse):
    """包含任务信息的执行日志响应模型"""
    task: Annotated[Optional[ScheduledTaskResponse], Field(None, description="关联的任务信息")]


# 响应类型定义
ScheduledTaskListResponse = ResponseData[List[ScheduledTaskResponse]]
ScheduledTaskDetailResponse = ResponseData[ScheduledTaskResponse]
TaskExecutionLogListResponse = ResponseData[List[TaskExecutionLogResponse]]
TaskExecutionLogDetailResponse = ResponseData[TaskExecutionLogResponse]
TaskExecutionLogCreateResponse = ResponseData[TaskExecutionLogResponse]
