"""Redis服务类"""
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
import asyncio
import redis.asyncio as redis
from redis.exceptions import LockError, LockNotOwnedError
from app.core.config import settings
from app.core.event_bus import ProductionEventBus
from app.models.redis_models import CallRecord, DialogRecord

# 使用主应用的logger
from app.core.logger import get_logger
from app.services.base_service import BaseService

logger = get_logger(__name__)


class RedisService(BaseService):
    """Redis 服务类 - 统一管理设备信息和电话记录（支持分布式锁）"""

    # Redis 键名常量
    DEVICE_INFO_KEY = "device_info"
    CALL_RECORD_PREFIX = "call_record:"
    LOCK_PREFIX = "lock:"
    CONFIG_INPUT_AUDIO_KEY = "config_input_audio"

    def __init__(self, event_bus: ProductionEventBus):
        """初始化 Redis 服务（支持事件总线注入）"""
        super().__init__(event_bus, "RedisService")
        self.redis_client: redis.Redis | None = None
        self._connection_pool: Optional[redis.ConnectionPool] = None
        self._initialized = False
        self.event_bus = event_bus

        # 锁配置
        self.lock_timeout = 10  # 锁超时时间（秒）
        self.blocking_timeout = 5  # 获取锁的阻塞超时时间（秒）

    async def initialize(self) -> bool:
        """异步初始化 Redis 连接"""
        if self._initialized:
            return True

        try:
            # 创建连接池
            self._connection_pool = redis.ConnectionPool(
                host=settings.redis_host,
                port=settings.redis_port,
                username=settings.redis_username,
                password=settings.redis_password,
                db=settings.redis_db,
                connection_class=redis.SSLConnection,
                # 连接配置
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                # 连接池配置
                max_connections=20,  # 添加最大连接数
                retry_on_error=[redis.ConnectionError],  # 添加重试错误类型
            )

            # 创建 Redis 客户端
            self.redis_client = redis.Redis(connection_pool=self._connection_pool)

            # 测试连接
            await self.redis_client.ping()
            self._initialized = True
            logger.info(
                "✅ Redis service initialized successfully with distributed lock support"
            )

            return True
        except Exception as e: # pylint: disable=broad-except
            logger.error("❌ Redis service initialization failed: %s", e)
            return False

    async def register_event_listeners(self):
        """注册事件监听器"""
        # await self._register_listener(EventType.REDIS_ADD_DIALOG_RECORD, self.add_dialog_record)

    async def shutdown(self):
        """异步关闭 Redis 连接"""
        try:
            if self.redis_client:
                self.redis_client.close()
                self.redis_client = None
                logger.info("Redis client closed")

            if self._connection_pool:
                self._connection_pool.disconnect()
                self._connection_pool = None
                logger.info("Redis connection pool closed")

            self._initialized = False

            logger.info("✅ Redis service shutdown completed")
        except Exception as e: # pylint: disable=broad-except
            logger.error("❌ Error during Redis shutdown: %s", e)

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            if not self._initialized or not self.redis_client:
                return {"status": "unhealthy", "error": "Not initialized"}

            # 测试连接
            await self.redis_client.ping()

            # 获取连接信息
            info = await self.redis_client.info()
            return {
                "status": "healthy",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "redis_version": info.get("redis_version", "unknown"),
            }
        except Exception as e: # pylint: disable=broad-except
            return {"status": "unhealthy", "error": str(e)}

    def _ensure_connected(self):
        """确保 Redis 已连接"""
        if not self._initialized or not self.redis_client:
            raise RuntimeError("Redis service not initialized")

    # ==================== 分布式锁管理 ====================

    @asynccontextmanager
    async def acquire_lock(
        self,
        resource_id: str,
        timeout: Optional[int] = None,
        blocking_timeout: Optional[int] = None,
    ):
        """
        获取Redis分布式锁的异步上下文管理器

        Args:
            resource_id: 资源ID，用于生成锁键名
            timeout: 锁超时时间（秒），默认使用实例配置
            blocking_timeout: 获取锁的阻塞超时时间（秒），默认使用实例配置
        """
        self._ensure_connected()

        lock_key = f"{self.LOCK_PREFIX}{resource_id}"
        lock_timeout = timeout or self.lock_timeout
        lock_blocking_timeout = blocking_timeout or self.blocking_timeout

        lock = None
        try:
            if self.redis_client is None:
                raise RuntimeError("Redis client does not support lock operation")
            lock = self.redis_client.lock(
                lock_key,
                timeout=lock_timeout,
                blocking_timeout=lock_blocking_timeout,
                thread_local=False,
            )

            # 在线程池中获取锁（避免阻塞事件循环）
            loop = asyncio.get_event_loop()
            acquired = await loop.run_in_executor(
                None, lambda: lock.acquire(blocking=True)
            )

            if not acquired:
                raise TimeoutError(f"Failed to acquire lock: {lock_key}")

            logger.debug("🔒 Lock acquired: %s", lock_key)
            yield lock

        except (LockError, LockNotOwnedError) as e:
            logger.error("❌ Lock error for %s: %s", lock_key, e)
            raise
        except TimeoutError as e:
            logger.error("⏰ Lock timeout for %s: %s", lock_key, e)
            raise
        except Exception as e:  # pylint: disable=broad-except
            logger.error("❌ Unexpected error acquiring lock %s: %s", lock_key, e)
            raise
        finally:
            if lock:
                try:
                    # 在线程池中释放锁
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, lock.release)
                    logger.debug("🔓 Lock released: %s", lock_key)
                except (LockError, LockNotOwnedError) as e:
                    logger.error("❌ Failed to release lock %s: %s", lock_key, e)
                except Exception as e:  # pylint: disable=broad-except
                    logger.error("❌ Unexpected error releasing lock %s: %s", lock_key, e)

    @asynccontextmanager
    async def _acquire_multiple_locks(
        self, resource_ids: List[str], timeout: Optional[int] = None
    ):
        """
        获取多个Redis分布式锁的异步上下文管理器

        Args:
            resource_ids: 资源ID列表
            timeout: 锁超时时间
        """
        # 对资源ID排序，避免死锁
        sorted_resource_ids = sorted(resource_ids)
        acquired_locks = []

        try:
            # 按顺序获取所有锁
            for resource_id in sorted_resource_ids:
                lock_key = f"{self.LOCK_PREFIX}{resource_id}"
                lock_timeout = timeout or self.lock_timeout

                if self.redis_client is None:
                    raise RuntimeError("Redis client is not initialized")

                lock = self.redis_client.lock(
                    lock_key,
                    timeout=lock_timeout,
                    blocking_timeout=self.blocking_timeout,
                    thread_local=False,
                )

                # 在线程池中获取锁
                loop = asyncio.get_event_loop()
                acquired = await loop.run_in_executor(None, lock.acquire, True)
                if not acquired:
                    raise TimeoutError(f"Failed to acquire lock: {lock_key}")

                acquired_locks.append(lock)
                logger.debug("🔒 Multi-lock acquired: %s", lock_key)

            yield acquired_locks

        except Exception as e:  # pylint: disable=broad-except
            logger.error("❌ Error acquiring multiple locks: %s", e)
            # 释放已获取的锁
            for lock in acquired_locks:
                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, lock.release)
                except Exception as release_error:  # pylint: disable=broad-except
                    logger.error(
                        "❌ Failed to release lock during cleanup: %s", release_error
                    )
            raise
        finally:
            # 释放所有锁
            for lock in acquired_locks:
                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, lock.release)
                    logger.debug("🔓 Multi-lock released")
                except (LockError, LockNotOwnedError) as e:
                    logger.error("❌ Failed to release multi-lock: %s", e)
                except Exception as e:  # pylint: disable=broad-except
                    logger.error("❌ Unexpected error releasing multi-lock: %s", e)

    async def get_call_record(
        self, call_id: str, lock: bool = True
    ) -> Optional[CallRecord]:
        """
        获取电话记录

        Args:
            call_id: 电话记录ID

        Returns:
            CallRecord: 电话记录对象，不存在时返回 None
        """
        self._ensure_connected()
        try:
            if lock:
                async with self.acquire_lock(f"{self.CALL_RECORD_PREFIX}{call_id}"):
                    return await self._get_call_record_without_lock(call_id)
            else:
                return await self._get_call_record_without_lock(call_id)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to get call record: %s", e)
            return None

    async def _get_call_record_without_lock(self, call_id: str) -> Optional[CallRecord]:
        """
        内部方法：获取电话记录
        """
        self._ensure_connected()
        try:
            key = f"{self.CALL_RECORD_PREFIX}{call_id}"
            if self.redis_client is None:
                raise RuntimeError("Redis client is not initialized")
            data = await self.redis_client.get(key)

            if not data:
                logger.warning("Call record not found: %s", call_id)
                return None

            call_record = CallRecord.model_validate_json(data)
            logger.info("Call record retrieved: %s", call_id)
            return call_record
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to get call record: %s", e)
            return None

    async def get_all_call_records(self) -> List[CallRecord]:
        """获取所有电话记录"""
        self._ensure_connected()
        try:
            pattern = f"{self.CALL_RECORD_PREFIX}*"
            if self.redis_client is None:
                raise RuntimeError("Redis client is not initialized")
            keys: List[str] = await self.redis_client.keys(pattern)

            records = []
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    records.append(CallRecord.model_validate_json(data))

            logger.info("All call records retrieved, total: %s", len(records))
            return records
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to get all call records: %s", e)
            return []

    # ==================== 对话记录管理 ====================

    async def create_dialog_record(self, dialog_record: DialogRecord) -> bool:
        """
        创建对话记录 - 使用分布式锁
        """
        self._ensure_connected()
        try:
            async with self.acquire_lock(
                f"{self.DIALOG_RECORD_PREFIX}{dialog_record.call_id}"
            ):
                if self.redis_client is None:
                    raise RuntimeError("Redis client is not initialized")
                await self.redis_client.set(
                    f"{self.DIALOG_RECORD_PREFIX}{dialog_record.call_id}",
                    dialog_record.model_dump_json(),
                    ex=86400,
                )
                return True
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to create dialog record: %s", e)
            return False

