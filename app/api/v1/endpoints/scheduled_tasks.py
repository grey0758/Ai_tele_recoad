"""
定时任务相关API端点

提供定时任务和任务执行日志的API接口
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_scheduled_tasks_service
from app.services.scheduled_tasks_service import ScheduledTasksService
from app.schemas.scheduled_tasks import (
    TaskExecutionLogCreate,
    ScheduledTaskDetailResponse,
    TaskExecutionLogCreateResponse
)
from app.schemas.base import ResponseBuilder

router = APIRouter()


@router.get("/scheduled-task/{task_id}", response_model=ScheduledTaskDetailResponse, summary="获取单个定时任务")
async def get_scheduled_task(
    task_id: int,
    scheduled_tasks_service: ScheduledTasksService = Depends(get_scheduled_tasks_service)
):
    """
    根据ID获取单个定时任务配置
    
    Args:
        task_id: 任务ID
        
    Returns:
        ScheduledTaskResponse: 定时任务详情
    """
    try:
        task = await scheduled_tasks_service.get_scheduled_task_by_id(task_id)
        
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"任务ID {task_id} 不存在"
            )
        
        return ResponseBuilder.success(
            data=task,
            message="获取定时任务详情成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取定时任务详情失败: {str(e)}"
        )


@router.post("/task-execution-logs", response_model=TaskExecutionLogCreateResponse, summary="创建任务执行日志")
async def create_task_execution_log(
    log_data: TaskExecutionLogCreate,
    scheduled_tasks_service: ScheduledTasksService = Depends(get_scheduled_tasks_service)
):
    """
    创建任务执行日志记录
    
    Args:
        log_data: 任务执行日志数据
        
    Returns:
        TaskExecutionLogResponse: 创建的执行日志
    """
    try:
        log_response = await scheduled_tasks_service.create_task_execution_log(log_data)
        
        return ResponseBuilder.success(
            data=log_response,
            message="创建任务执行日志成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建任务执行日志失败: {str(e)}"
        )
