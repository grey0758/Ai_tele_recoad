"""
aiBox 服务层

提供顾问通话时长统计相关的业务逻辑处理
"""

from typing import Optional
from datetime import date
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert

from app.core.event_bus import ProductionEventBus
from app.db.database import Database
from app.services.base_service import BaseService
from app.models.advisor_call_duration_stats import AdvisorCallDurationStats, AdvisorDeviceConfig
from app.schemas.advisor_call_duration_stats import (
    AdvisorCallDurationStatsUpsertRequest
)
from app.core.logger import get_logger

logger = get_logger(__name__)


class AiBoxService(BaseService):
    """aiBox 服务类"""
    
    def __init__(self, event_bus: ProductionEventBus, database: Database):
        super().__init__(event_bus=event_bus, service_name="AiBoxService")
        self.database = database
    
    async def initialize(self) -> bool:
        return True
    
    async def upsert_advisor_call_duration_stats(
        self, 
        stats_data: AdvisorCallDurationStatsUpsertRequest
    ) -> AdvisorCallDurationStats:
        """
        更新或插入顾问通话时长统计
        
        如果 UNIQUE KEY (advisor_id, stats_date) 存在则更新，否则插入
        """
        async with self.database.get_session() as db_session:
            try:
                #通过设备ID获取顾问ID和顾问姓名
                advisor_id, advisor_name = await self._get_advisor_id_by_device_id(db_session, stats_data.device_id)
                if not advisor_id:
                    raise ValueError(f"设备ID {stats_data.device_id} 对应的顾问ID不存在")
                stats_data.advisor_id = advisor_id
                stats_data.advisor_name = advisor_name

                # 检查记录是否存在
                existing_stats = await self._get_stats_by_advisor_and_date(
                    db_session, stats_data.advisor_id, stats_data.stats_date
                )
                
                if existing_stats:
                    # 更新现有记录
                    update_data = stats_data.model_dump(exclude_unset=True)
                    for field, value in update_data.items():
                        setattr(existing_stats, field, value)
                    
                    await db_session.commit()
                    await db_session.refresh(existing_stats)
                    
                    logger.info(
                        "成功更新顾问通话时长统计: advisor_id=%s, stats_date=%s", 
                        stats_data.advisor_id, stats_data.stats_date
                    )
                    return existing_stats
                else:
                    # 插入新记录
                    new_stats = AdvisorCallDurationStats(**stats_data.model_dump())
                    db_session.add(new_stats)
                    await db_session.commit()
                    await db_session.refresh(new_stats)
                    
                    logger.info(
                        "成功创建顾问通话时长统计: advisor_id=%s, stats_date=%s", 
                        stats_data.advisor_id, stats_data.stats_date
                    )
                    return new_stats
                    
            except Exception as e:
                await db_session.rollback()
                logger.error("更新或插入顾问通话时长统计失败: %s", e)
                raise
    
    async def get_advisor_call_duration_stats(
        self, 
        advisor_id: int, 
        stats_date: date
    ) -> Optional[AdvisorCallDurationStats]:
        """根据顾问ID和统计日期获取通话时长统计"""
        async with self.database.get_session() as db_session:
            try:
                return await self._get_stats_by_advisor_and_date(
                    db_session, advisor_id, stats_date
                )
            except Exception as e:
                logger.error("获取顾问通话时长统计失败: %s", e)
                return None
    
    async def get_advisor_stats_by_date_range(
        self, 
        advisor_id: int, 
        start_date: date, 
        end_date: date
    ) -> list[AdvisorCallDurationStats]:
        """根据顾问ID和日期范围获取通话时长统计列表"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(AdvisorCallDurationStats)
                    .where(
                        and_(
                            AdvisorCallDurationStats.advisor_id == advisor_id,
                            AdvisorCallDurationStats.stats_date >= start_date,
                            AdvisorCallDurationStats.stats_date <= end_date
                        )
                    )
                    .order_by(AdvisorCallDurationStats.stats_date.desc())
                )
                return list(result.scalars().all())
            except Exception as e:
                logger.error("根据日期范围获取顾问通话时长统计失败: %s", e)
                return []
    
    async def get_all_advisor_stats_by_date(
        self, 
        stats_date: date
    ) -> list[AdvisorCallDurationStats]:
        """根据指定日期获取所有顾问的通话时长统计列表"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(AdvisorCallDurationStats)
                    .where(AdvisorCallDurationStats.stats_date == stats_date)
                    .order_by(AdvisorCallDurationStats.advisor_id.asc())
                )
                return list(result.scalars().all())
            except Exception as e:
                logger.error("根据日期获取所有顾问通话时长统计失败: %s", e)
                return []
    
    async def _get_stats_by_advisor_and_date(
        self, 
        db_session: AsyncSession, 
        advisor_id: int, 
        stats_date: date
    ) -> Optional[AdvisorCallDurationStats]:
        """在指定会话中根据顾问ID和统计日期获取统计记录"""
        result = await db_session.execute(
            select(AdvisorCallDurationStats).where(
                and_(
                    AdvisorCallDurationStats.advisor_id == advisor_id,
                    AdvisorCallDurationStats.stats_date == stats_date
                )
            )
        )
        return result.scalar_one_or_none()

    async def _get_advisor_id_by_device_id(
        self, 
        db_session: AsyncSession, 
        device_id: str
    ) -> tuple[int, str]:
        """根据设备ID获取顾问ID和顾问姓名"""
        result = await db_session.execute(
            select(AdvisorDeviceConfig.advisor_id, AdvisorDeviceConfig.advisor_name).where(
                AdvisorDeviceConfig.device_id == device_id
            )
        )
        row = result.first()
        if row:
            return row.advisor_id, row.advisor_name
        else:
            return None, None