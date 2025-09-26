"""
调度器服务

基于APScheduler的定时任务调度服务，用于内部调用
提供定时任务管理、执行监控和状态管理功能
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import (
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ERROR,
    EVENT_JOB_MISSED,
)
from apscheduler.jobstores.base import JobLookupError
from app.models.events import EventType
from app.core.event_bus import ProductionEventBus
from app.db.database import Database
from app.services.aibox_service import Aiboxservice
from app.services.base_service import BaseService
from app.services.scheduled_tasks_service import ScheduledTasksService
from app.core.logger import get_logger

logger = get_logger(__name__)


class SchedulerService(BaseService):
    """调度器服务类"""

    def __init__(
        self,
        event_bus: ProductionEventBus,
        database: Database,
        scheduled_tasks_service: ScheduledTasksService,
        aibox_service: Aiboxservice,
    ):
        super().__init__(event_bus=event_bus, service_name="SchedulerService")
        self.database = database
        self.scheduler: Optional[BackgroundScheduler] = None
        self.scheduler_running = False
        self.scheduled_tasks_service = scheduled_tasks_service
        self.aibox_service = aibox_service
        # 任务执行状态
        self.job_status: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> bool:
        """初始化调度器服务"""
        try:
            # 获取定时任务服务
            if not self.event_bus:
                raise RuntimeError("EventBus not initialized")

            # 创建调度器
            self.scheduler = BackgroundScheduler()

            # 添加事件监听器
            self.scheduler.add_listener(
                self._job_listener,
                EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED,
            )

            # 启动调度器
            await self.start_scheduler()

            logger.info("调度器服务初始化成功")
            return True

        except Exception as e:  # pylint: disable=broad-except
            logger.error("调度器服务初始化失败: %s", str(e))
            return False

    async def start_scheduler(self) -> bool:
        """启动调度器"""
        if self.scheduler_running:
            logger.warning("调度器已在运行中")
            return True

        try:
            # 启动调度器
            if self.scheduler:
                self.scheduler.start()
            self.scheduler_running = True

            # 加载并启动所有活跃的定时任务
            await self._load_and_start_tasks()

            logger.info("调度器启动成功")
            return True

        except Exception as e:  # pylint: disable=broad-except
            logger.error("启动调度器失败: %s", str(e))
            return False

    async def stop_scheduler(self) -> bool:
        """停止调度器"""
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown(wait=False)

            self.scheduler_running = False
            self.job_status.clear()

            logger.info("调度器已停止")
            return True

        except Exception as e:  # pylint: disable=broad-except
            logger.error("停止调度器失败: %s", str(e))
            return False

    async def add_job(self, job_id: str, func, trigger, **kwargs) -> bool:
        """添加定时任务"""
        try:
            if not self.scheduler or not self.scheduler.running:
                logger.error("调度器未运行，无法添加任务")
                return False

            self.scheduler.add_job(func=func, trigger=trigger, id=job_id, **kwargs)

            # 更新任务状态
            self.job_status[job_id] = {
                "status": "scheduled",
                "added_at": datetime.now(),
                "last_run": None,
                "next_run": None,
                "run_count": 0,
                "error_count": 0,
            }

            logger.info("任务 %s 添加成功", job_id)
            return True

        except Exception as e:  # pylint: disable=broad-except
            logger.error("添加任务 %s 失败: %s", job_id, str(e))
            return False

    async def remove_job(self, job_id: str) -> bool:
        """移除定时任务"""
        try:
            if not self.scheduler or not self.scheduler.running:
                logger.warning("调度器未运行")
                return False

            self.scheduler.remove_job(job_id)

            # 移除任务状态
            if job_id in self.job_status:
                del self.job_status[job_id]

            logger.info("任务 %s 移除成功", job_id)
            return True

        except JobLookupError:
            logger.warning("任务 %s 不存在", job_id)
            return False
        except Exception as e:  # pylint: disable=broad-except
            logger.error("移除任务 %s 失败: %s", job_id, str(e))
            return False

    async def get_job_status(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """获取任务状态"""
        if job_id:
            return self.job_status.get(job_id, {})
        return self.job_status.copy()

    async def get_scheduler_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        if not self.scheduler:
            return {"status": "not_initialized", "running": False}

        jobs = []
        if self.scheduler.running:
            for job in self.scheduler.get_jobs():
                jobs.append(
                    {
                        "id": job.id,
                        "name": job.name,
                        "next_run_time": job.next_run_time.isoformat()
                        if job.next_run_time
                        else None,
                        "trigger": str(job.trigger),
                    }
                )

        return {
            "status": "running" if self.scheduler_running else "stopped",
            "running": self.scheduler_running,
            "job_count": len(jobs),
            "jobs": jobs,
            "job_status": self.job_status,
        }

    async def _load_and_start_tasks(self):
        """加载并启动所有活跃的定时任务"""
        try:
            if not self.scheduled_tasks_service:
                logger.error("定时任务服务未初始化")
                return

            # 获取所有活跃的定时任务
            tasks = await self.scheduled_tasks_service.get_all_scheduled_tasks()

            for task in tasks:
                if (
                    task.is_active
                    and task.cron_expression
                    and task.task_type == "data_sync_service"
                ):
                    try:
                        # 解析cron表达式
                        trigger = CronTrigger.from_crontab(task.cron_expression)

                        # 添加任务
                        await self.add_job(
                            job_id=f"task_{task.id}",
                            func=self._execute_advisor_stats_task,
                            trigger=trigger,
                            args=[task.id, task.task_name],
                            name=task.task_name,
                        )

                        logger.info("定时任务 %s 已启动", task.task_name)

                    except Exception as e:  # pylint: disable=broad-except
                        logger.error("启动定时任务 %s 失败: %s", task.task_name, str(e))

        except Exception as e:  # pylint: disable=broad-except
            logger.error("加载定时任务失败: %s", str(e))

    def _execute_advisor_stats_task(self, task_id: int, task_name: str):
        """执行顾问统计数据任务"""
        try:
            logger.info("开始执行定时任务: %s (ID: %s)", task_name, task_id)

            # 更新任务状态
            job_id = f"task_{task_id}"
            if job_id in self.job_status:
                self.job_status[job_id]["last_run"] = datetime.now()
                self.job_status[job_id]["run_count"] += 1

            try:
                asyncio.run(
                    self.emit_event(EventType.SEND_ADVISOR_STATS_WECHAT_REPORT_TASK)
                )
            finally:
                pass

            logger.info("定时任务 %s 执行完成", task_name)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("执行定时任务 %s 失败: %s", task_name, str(e))

            # 更新错误计数
            job_id = f"task_{task_id}"
            if job_id in self.job_status:
                self.job_status[job_id]["error_count"] += 1

    def _job_listener(self, event):
        """任务执行监听器"""
        job_id = event.job_id

        if event.exception:
            logger.error("任务 %s 执行失败: %s", job_id, str(event.exception))
            if job_id in self.job_status:
                self.job_status[job_id]["error_count"] += 1
        else:
            logger.info("任务 %s 执行成功", job_id)
            if job_id in self.job_status:
                self.job_status[job_id]["last_run"] = datetime.now()
                self.job_status[job_id]["run_count"] += 1

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            status = await self.get_scheduler_status()
            return {
                "status": "healthy" if status["running"] else "stopped",
                "scheduler_running": status["running"],
                "job_count": status["job_count"],
                "last_check": datetime.now().isoformat(),
            }
        except Exception as e:  # pylint: disable=broad-except
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat(),
            }

    async def shutdown(self):
        """关闭服务"""
        await self.stop_scheduler()
        logger.info("调度器服务已关闭")
