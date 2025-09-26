"""
定时任务服务层

提供定时任务和任务执行日志相关的业务逻辑处理
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.event_bus import ProductionEventBus
from app.db.database import Database
from app.services.base_service import BaseService
from app.models.scheduled_tasks import ScheduledTasks, TaskExecutionLogs
from app.schemas.scheduled_tasks import (
    ScheduledTaskResponse,
    TaskExecutionLogCreate,
    TaskExecutionLogResponse,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


class ScheduledTasksService(BaseService):
    """定时任务服务类"""

    def __init__(self, event_bus: ProductionEventBus, database: Database):
        super().__init__(event_bus=event_bus, service_name="ScheduledTasksService")
        self.database = database

    async def initialize(self) -> bool:
        return True

    async def get_all_scheduled_tasks(self) -> List[ScheduledTaskResponse]:
        """获取所有定时任务配置"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(select(ScheduledTasks))
                tasks = result.scalars().all()

                task_responses = [
                    ScheduledTaskResponse.model_validate(task) for task in tasks
                ]

                logger.info("成功获取 %s 个定时任务", len(tasks))
                return task_responses

            except Exception as e:
                logger.error("获取定时任务列表失败: %s", str(e))
                raise

    async def get_scheduled_task_by_id(
        self, task_id: int
    ) -> Optional[ScheduledTaskResponse]:
        """根据ID获取定时任务"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(ScheduledTasks).where(ScheduledTasks.id == task_id)
                )
                task = result.scalar_one_or_none()

                if task:
                    return ScheduledTaskResponse.model_validate(task)
                return None

            except Exception as e:
                logger.error("获取定时任务失败: %s", str(e))
                raise

    async def create_task_execution_log(
        self, log_data: TaskExecutionLogCreate
    ) -> TaskExecutionLogResponse:
        """创建任务执行日志"""
        async with self.database.get_session() as db_session:
            try:
                # 验证任务是否存在
                task = await self._get_task_by_id_with_session(
                    db_session, log_data.task_id
                )
                if not task:
                    raise ValueError(f"任务ID {log_data.task_id} 不存在")

                # 创建执行日志
                execution_log = TaskExecutionLogs(
                    task_id=log_data.task_id,
                    advisor_id=log_data.advisor_id,
                    execution_time=log_data.execution_time,
                    status=log_data.status,
                    error_message=log_data.error_message,
                    execution_duration=log_data.execution_duration,
                )

                db_session.add(execution_log)
                await db_session.commit()
                await db_session.refresh(execution_log)

                log_response = TaskExecutionLogResponse.model_validate(execution_log)

                logger.info(
                    "成功创建任务执行日志: task_id=%s, status=%s",
                    log_data.task_id,
                    log_data.status,
                )
                return log_response

            except Exception as e:
                await db_session.rollback()
                logger.error("创建任务执行日志失败: %s", str(e))
                raise

    async def get_task_execution_logs_by_task_id(
        self, task_id: int, limit: int = 50
    ) -> List[TaskExecutionLogResponse]:
        """根据任务ID获取执行日志列表"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(TaskExecutionLogs)
                    .where(TaskExecutionLogs.task_id == task_id)
                    .order_by(TaskExecutionLogs.created_at.desc())
                    .limit(limit)
                )
                logs = result.scalars().all()

                log_responses = [
                    TaskExecutionLogResponse.model_validate(log) for log in logs
                ]

                logger.info(
                    "成功获取任务 %s 的 %s 条执行日志",
                    task_id,
                    len(log_responses),
                )
                return log_responses

            except Exception as e:
                logger.error("获取任务执行日志失败: %s", str(e))
                raise

    async def get_task_execution_logs_by_advisor_id(
        self, advisor_id: int, limit: int = 50
    ) -> List[TaskExecutionLogResponse]:
        """根据顾问ID获取执行日志列表"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(TaskExecutionLogs)
                    .where(TaskExecutionLogs.advisor_id == advisor_id)
                    .order_by(TaskExecutionLogs.created_at.desc())
                    .limit(limit)
                )
                logs = result.scalars().all()

                log_responses = [
                    TaskExecutionLogResponse.model_validate(log) for log in logs
                ]

                logger.info(
                    "成功获取顾问 %s 的 %s 条执行日志",
                    advisor_id,
                    len(log_responses),
                )
                return log_responses

            except Exception as e:
                logger.error("获取顾问执行日志失败: %s", str(e))
                raise

    async def get_all_task_execution_logs(
        self, limit: int = 100
    ) -> List[TaskExecutionLogResponse]:
        """获取所有任务执行日志"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(TaskExecutionLogs)
                    .order_by(TaskExecutionLogs.created_at.desc())
                    .limit(limit)
                )
                logs = result.scalars().all()

                log_responses = [
                    TaskExecutionLogResponse.model_validate(log) for log in logs
                ]

                logger.info("成功获取 %s 条执行日志", len(log_responses))
                return log_responses

            except Exception as e:
                logger.error("获取所有执行日志失败: %s", str(e))
                raise

    # 私有辅助方法
    async def _get_task_by_id_with_session(
        self, db_session: AsyncSession, task_id: int
    ) -> Optional[ScheduledTasks]:
        """在指定会话中根据ID获取定时任务"""
        result = await db_session.execute(
            select(ScheduledTasks).where(ScheduledTasks.id == task_id)
        )
        return result.scalar_one_or_none()
