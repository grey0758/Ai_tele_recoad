
# app/core/dependencies.py
"""
服务容器 - 支持事件总线和生命周期管理
"""
from datetime import datetime
from typing import Optional, Dict, Any
import asyncio
from fastapi import HTTPException, status
from app.core.event_bus import ProductionEventBus, create_event_bus
from app.core.config import settings
from app.core.logger import get_logger
from app.services.lead_service import LeadService
from app.services.upload_record_service import FileService
from app.services.aibox_service import Aiboxservice
from app.services.scheduled_tasks_service import ScheduledTasksService
from app.services.scheduler_service import SchedulerService
from app.db.database import Database

logger = get_logger(__name__)


class EnhancedServiceContainer:
    """增强的服务容器 - 支持事件总线和生命周期管理"""

    def __init__(self) -> None:
        self._services: Dict[str, Any] = {}
        self._event_bus: Optional[ProductionEventBus] = None
        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> bool:
        """初始化所有服务"""
        if self._initialized:
            return True

        async with self._lock:
            if self._initialized:  # 双重检查
                return True

            try:
                logger.info("Initializing service container...")

                # 1. 首先初始化事件总线
                self._event_bus = create_event_bus(settings)
                await self._event_bus.start()
                logger.info("✅ EventBus initialized")

                # 2. 初始化业务服务（注入事件总线）
                await self._initialize_services()
                logger.info("✅ Business services initialized")

                # 3. 注册事件监听器
                await self._register_event_listeners()
                logger.info("✅ Event listeners registered")

                self._initialized = True
                logger.info("🎉 Service container initialization completed")

                return True

            except Exception as e: # pylint: disable=broad-except
                logger.error(
                    "❌ Service container initialization failed | error=%s", str(e)
                )
                await self._cleanup()
                return False

    async def _initialize_services(self):
        """初始化业务服务"""
        self._services["db_service"] = Database()
        self._services["file_service"] = FileService(self._event_bus)
        self._services["lead_service"] = LeadService(self._event_bus, self._services["db_service"])
        self._services["aibox_service"] = Aiboxservice(self._event_bus, self._services["db_service"])
        self._services["scheduled_tasks_service"] = ScheduledTasksService(self._event_bus, self._services["db_service"])
        self._services["scheduler_service"] = SchedulerService(self._event_bus, self._services["db_service"], self._services["scheduled_tasks_service"], self._services["aibox_service"])

        for name, service in self._services.items():
            if hasattr(service, "initialize"):
                success = await service.initialize()
                if success:
                    logger.info("✅ Service %s initialized", name)
                else:
                    logger.error("❌ Service %s initialization failed", name)
                    if name == "db_service":
                        raise RuntimeError(
                            f"Critical service {name} failed to initialize"
                        )

    async def _register_event_listeners(self):
        """注册所有服务的事件监听器"""
        for name, service in self._services.items():
            if hasattr(service, "register_event_listeners"):
                await service.register_event_listeners()
                logger.info("Event listeners registered for %s", name)

    async def shutdown(self):
        """关闭所有服务"""
        if not self._initialized:
            return

        logger.info("Shutting down service container...")

        try:
            # 1. 关闭业务服务
            for name, service in self._services.items():
                if hasattr(service, "shutdown"):
                    try:
                        await service.shutdown()
                        logger.info("Service %s shutdown completed", name)
                    except Exception as e: # pylint: disable=broad-except
                        logger.error("Error shutting down %s | error=%s", name, str(e))

            # 2. 关闭事件总线
            if self._event_bus and self._event_bus.running:
                await self._event_bus.stop()
                logger.info("EventBus shutdown completed")

        except Exception as e: # pylint: disable=broad-except
            logger.error("Error during shutdown | error=%s", str(e))
        finally:
            await self._cleanup()

    async def _cleanup(self):
        """清理资源"""
        self._services.clear()
        self._event_bus = None
        self._initialized = False

    def register_service(self, name: str, service):
        """注册服务"""
        self._services[name] = service

    def get_service(self, name: str):
        """获取服务"""
        if not self._initialized:
            raise RuntimeError("Service container not initialized")
        return self._services.get(name)

    def get_event_bus(self) -> ProductionEventBus:
        """获取事件总线"""
        if not self._initialized or not self._event_bus:
            raise RuntimeError("EventBus not initialized")
        return self._event_bus

    def get_all_services(self):
        """获取所有服务"""
        return self._services.copy()

    @property
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized

    @property
    def is_event_bus_running(self) -> bool:
        """检查事件总线是否运行中"""
        return bool(self._initialized and self._event_bus and self._event_bus.running)


# 全局服务容器
service_container = EnhancedServiceContainer()

# === FastAPI 依赖注入函数 ===

# def get_event_bus() -> ProductionEventBus:
#     """获取事件总线依赖"""
#     try:
#         if not service_container.is_event_bus_running:
#             raise HTTPException(
#                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 detail="Event bus is not running"
#             )
#         return service_container.get_event_bus()
#     except RuntimeError as e:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail=str(e)
#         )


# === 批量获取服务 ===
def get_database() -> Database:
    """获取数据库服务"""
    return service_container.get_service("db_service")


def get_file_service() -> FileService:
    """获取文件服务"""
    return service_container.get_service("file_service")


def get_lead_service() -> LeadService:
    """获取线索服务"""
    return service_container.get_service("lead_service")


def get_aibox_service() -> Aiboxservice:
    """获取aiBox服务"""
    return service_container.get_service("aibox_service")


def get_scheduled_tasks_service() -> ScheduledTasksService:
    """获取定时任务服务"""
    return service_container.get_service("scheduled_tasks_service")


def get_scheduler_service() -> SchedulerService:
    """获取调度器服务"""
    return service_container.get_service("scheduler_service")


def get_all_services() -> Dict[str, Any]:
    """获取所有服务"""
    if not service_container.is_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Services not initialized",
        )
    return service_container.get_all_services()


# === 健康检查 ===


async def check_services_health() -> Dict[str, Any]:
    """检查所有服务健康状态"""
    if not service_container.is_initialized:
        return {"status": "not_initialized", "services": {}}

    health_status: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {},
    }

    # 检查事件总线
    try:
        event_bus = service_container.get_event_bus()
        bus_health = await event_bus.get_health_status()
        health_status["services"]["event_bus"] = bus_health
    except Exception as e: # pylint: disable=broad-except
        health_status["services"]["event_bus"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "degraded"

    # 检查业务服务
    for name, service in service_container.get_all_services().items():
        try:
            if hasattr(service, "health_check"):
                service_health = await service.health_check()
                health_status["services"][name] = service_health
            else:
                health_status["services"][name] = {"status": "unknown"}
        except Exception as e: # pylint: disable=broad-except
            health_status["services"][name] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"

    return health_status
