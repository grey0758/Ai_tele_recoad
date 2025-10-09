"""
aiBox 服务层

提供顾问通话时长统计相关的业务逻辑处理
"""

from typing import Optional
from datetime import date
import httpx
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.events import Event, EventType
from app.core.event_bus import ProductionEventBus
from app.db.database import Database
from app.services.base_service import BaseService
from app.models.advisor_call_duration_stats import (
    AdvisorCallDurationStats,
    AdvisorDeviceConfig,
)
from app.models.advisors import Advisors
from app.schemas.advisor_call_duration_stats import (
    AdvisorCallDurationStatsUpdateRequestWithDeviceIdAndStatsDate,
)
from app.models.events import EventPriority
from app.core.logger import get_logger
from app.core.config import settings
from app.core.exceptions import ExternalRequestException

logger = get_logger(__name__)


class Aiboxservice(BaseService):
    """aiox 服务类"""

    def __init__(self, event_bus: ProductionEventBus, database: Database):
        super().__init__(event_bus=event_bus, service_name="AiBoxService")
        self.database = database
        self.event_bus = event_bus

    async def initialize(self) -> bool:
        return True

    async def register_event_listeners(self):
        """注册事件监听器"""
        await self._register_listener(EventType.SEND_ADVISOR_STATS_WECHAT_REPORT_TASK, self.send_advisor_stats_wechat_report_task, priority=EventPriority.HIGH)

    async def upsert_advisor_call_duration_stats(
        self, stats_data: AdvisorCallDurationStatsUpdateRequestWithDeviceIdAndStatsDate
    ) -> AdvisorCallDurationStats:
        """
        更新或插入顾问通话时长统计

        如果 UNIQUE KEY (advisor_id, stats_date) 存在则更新，否则插入
        """
        async with self.database.get_session() as db_session:
            try:
                # 通过设备ID获取顾问ID和顾问姓名
                advisor_id, advisor_name, goal = await self._get_advisor_id_by_device_id(
                    db_session, stats_data.device_id
                )
                if not advisor_id and not advisor_name:
                    raise ValueError(f"设备ID {stats_data.device_id} 对应的顾问ID和顾问姓名不存在")
                stats_data.advisor_id = advisor_id
                stats_data.advisor_name = advisor_name
                stats_data.goal = goal

                # 检查记录是否存在
                existing_stats = await self._get_stats_by_advisor_and_date(
                    db_session, stats_data.advisor_id, stats_data.stats_date
                )

                if existing_stats:
                    # 更新现有记录
                    update_data = stats_data.model_dump(exclude_unset=True)

                    # 获取更新前的修正值并应用到新的 total_duration
                    if "total_duration" in update_data:
                        previous_correction = existing_stats.total_duration_correction or 0
                        new_duration = update_data["total_duration"]
                        update_data["total_duration"] = new_duration + previous_correction
                        update_data["total_duration_correction"] = previous_correction
                        logger.info(
                            "应用修正值到总时长: 新时长=%d秒, 修正值=%d秒, 修正后时长=%d秒",
                            new_duration,
                            previous_correction,
                            update_data["total_duration"],
                        )

                    for field, value in update_data.items():
                        setattr(existing_stats, field, value)

                    await db_session.commit()
                    await db_session.refresh(existing_stats)

                    logger.info(
                        "成功更新顾问通话时长统计: advisor_id=%s, stats_date=%s",
                        stats_data.advisor_id,
                        stats_data.stats_date,
                    )
                    return existing_stats
                else:
                    # 插入新记录
                    stats_dict = stats_data.model_dump()

                    # 新记录的修正值默认为0
                    stats_dict["total_duration_correction"] = 0

                    new_stats = AdvisorCallDurationStats(**stats_dict)
                    db_session.add(new_stats)
                    await db_session.commit()
                    await db_session.refresh(new_stats)

                    logger.info(
                        "成功创建顾问通话时长统计: advisor_id=%s, stats_date=%s",
                        stats_data.advisor_id,
                        stats_data.stats_date,
                    )
                    return new_stats

            except Exception as e:
                await db_session.rollback()
                logger.error("更新或插入顾问通话时长统计失败: %s", e)
                raise

    async def get_advisor_call_duration_stats(
        self, advisor_id: int, stats_date: date
    ) -> Optional[AdvisorCallDurationStats]:
        """根据顾问ID和统计日期获取通话时长统计"""
        async with self.database.get_session() as db_session:
            try:
                return await self._get_stats_by_advisor_and_date(
                    db_session, advisor_id, stats_date
                )
            except Exception as e:  # pylint: disable=broad-except
                logger.error("获取顾问通话时长统计失败: %s", e)
                return None

    async def get_advisor_stats_by_date_range(
        self, advisor_id: int, start_date: date, end_date: date
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
                            AdvisorCallDurationStats.stats_date <= end_date,
                        )
                    )
                    .order_by(AdvisorCallDurationStats.stats_date.desc())
                )
                return list(result.scalars().all())
            except Exception as e:  # pylint: disable=broad-except
                logger.error("根据日期范围获取顾问通话时长统计失败: %s", e)
                return []

    async def get_all_advisor_stats_by_date(
        self, stats_date: date = date.today()
    ) -> list[AdvisorCallDurationStats]:
        """获取指定日期的所有顾问通话时长统计"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(AdvisorCallDurationStats)
                    .where(AdvisorCallDurationStats.stats_date == stats_date)
                    .order_by(AdvisorCallDurationStats.advisor_id.asc())
                )
                return list(result.scalars().all())
            except Exception as e:  # pylint: disable=broad-except
                logger.error("获取指定日期所有顾问通话时长统计失败: %s", e)
                return []

    async def _get_stats_by_advisor_and_date(
        self, db_session: AsyncSession, advisor_id: int, stats_date: date
    ) -> Optional[AdvisorCallDurationStats]:
        """在指定会话中根据顾问ID和统计日期获取统计记录"""
        result = await db_session.execute(
            select(AdvisorCallDurationStats).where(
                and_(
                    AdvisorCallDurationStats.advisor_id == advisor_id,
                    AdvisorCallDurationStats.stats_date == stats_date,
                )
            )
        )
        return result.scalar_one_or_none()

    async def _get_advisor_id_by_device_id(
        self, db_session: AsyncSession, device_id: str
    ) -> tuple[int, str, int]:
        """根据设备ID获取顾问ID和顾问姓名"""
        result = await db_session.execute(
            select(
                AdvisorDeviceConfig.advisor_id, AdvisorDeviceConfig.advisor_name, AdvisorDeviceConfig.goal
            ).where(AdvisorDeviceConfig.device_id == device_id)
        )
        row = result.first()
        if row:
            return (row.advisor_id, row.advisor_name, row.goal)
        return (0, "", 0)

    async def send_wechat_message(
        self, to_wxid: str, message: str, authorization_token: str = ""
    ) -> str:
        """
        发送微信消息

        Args:
            to_wxid: 接收者的微信ID
            message: 要发送的消息内容
            authorization_token: 授权令牌

        Returns:
            str: 发送是否成功
        """
        url = settings.wechat_bot_url

        headers = {"Content-Type": "application/json"}

        # 将token放到params字段中
        params = {"token": authorization_token}

        data = {
            "to_wxid": to_wxid,
            "msg": {"text": message, "xml": "", "url": "", "name": "", "url_thumb": ""},
            "to_ren": "",
            "msg_type": 1,
            "send_type": 1,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url, headers=headers, json=data, params=params
                )

                if response.status_code == 200:
                    message = f"微信消息发送成功: to_wxid={to_wxid}"
                    logger.info(message)
                    return message
                else:
                    error_message = f"微信消息发送失败: status_code={response.status_code}, response={response.text}"
                    logger.error(error_message)
                    raise ExternalRequestException(error_message)

        except Exception as e:  # pylint: disable=broad-except
            error_message = f"微信消息发送异常: to_wxid={to_wxid}, error={str(e)}"
            logger.error(error_message)
            raise ExternalRequestException(error_message) from e

    # 发送顾问时长统计微信播报定时任务
    async def send_advisor_stats_wechat_report_task(self, _event: Event) -> str:
        """发送顾问时长统计微信播报定时任务"""
        stats_list = await self.get_all_advisor_stats_by_date(date.today())
        logger.info("发送顾问时长统计微信播报定时任务，共获取到 %d 条记录", len(stats_list))

        # 检查并更新指标完成状态，获取刚刚完成指标的顾问
        newly_completed_stats = await self._check_and_update_goal_completion(stats_list)

        # 过滤出未完成指标的顾问记录，以及刚刚完成指标的顾问（用于播报）
        filtered_stats_list = [stats for stats in stats_list if not stats.goal_completed_today] + newly_completed_stats
        logger.info("过滤后剩余 %d 条记录（未完成指标的顾问 + 刚刚完成指标的顾问）", len(filtered_stats_list))

        # 记录每个顾问的统计信息
        for stats in stats_list:
            logger.info(
                "顾问统计 - ID: %d, 姓名: %s, 日期: %s, 总通话时长: %d秒, 接通率: %.2f%%",
                stats.advisor_id,
                stats.advisor_name,
                stats.stats_date,
                stats.total_duration,
                float(stats.connection_rate) if stats.connection_rate else 0.0,
            )

        # 如果过滤后没有记录，则不播报
        if not filtered_stats_list:
            message = "所有顾问的指标都已完成，跳过微信播报发送"
            logger.info(message)
            return message

        # 生成微信播报消息
        msg_lines = ["=== 顾问待打时长统计 ==="]
        for stats in filtered_stats_list:
            # 计算待打时长
            target_duration_minutes = stats.goal / 60  # 转换为分钟
            current_duration_minutes = stats.total_duration / 60  # 转换为分钟
            remaining_minutes = max(
                0, target_duration_minutes - current_duration_minutes
            )

            msg_lines.append(f"\n顾问: {stats.advisor_name}")
            msg_lines.append(f"目标时长：{target_duration_minutes:.0f}分钟")
            msg_lines.append(f"当前时长：{current_duration_minutes:.1f}分钟")
            msg_lines.append(f"待打：{remaining_minutes:.1f}分钟")

        msg = "\n".join(msg_lines)
        logger.info("生成的微信播报消息:\n%s", msg)

        message = await self.send_wechat_message(
            to_wxid=settings.wechat_default_wxid,
            message=msg,
            authorization_token=settings.wechat_bot_token,
            )

        return message

    async def _check_and_update_goal_completion(self, stats_list: list[AdvisorCallDurationStats]) -> list[AdvisorCallDurationStats]:
        """检查并更新指标完成状态，返回刚刚完成指标的顾问列表"""
        newly_completed = []
        async with self.database.get_session() as db_session:
            try:
                for stats in stats_list:
                    # 检查是否达到指标且未标记为完成
                    if stats.total_duration >= stats.goal and not stats.goal_completed_today:
                        # 从当前会话中重新查询记录
                        current_stats = await self._get_stats_by_advisor_and_date(
                            db_session, stats.advisor_id, stats.stats_date
                        )
                        if current_stats:
                            # 更新指标完成状态
                            current_stats.goal_completed_today = True
                            newly_completed.append(stats)
                            logger.info(
                                "顾问 %s (ID: %d) 指标已完成，总时长: %d秒，目标: %d秒",
                                stats.advisor_name,
                                stats.advisor_id,
                                stats.total_duration,
                                stats.goal
                            )

                # 统一提交所有更新
                await db_session.commit()

                # 更新内存中的对象状态
                for stats in newly_completed:
                    stats.goal_completed_today = True

                return newly_completed
            except Exception as e:
                await db_session.rollback()
                logger.error("更新指标完成状态失败: %s", e)
                raise

    async def get_or_create_advisor_device_config(self, device_id: str, devid: str) -> AdvisorDeviceConfig:
        """
        通过device_id获取或创建顾问设备配置
        
        Args:
            device_id: 设备ID
            devid: 设备ID（新字段）
            
        Returns:
            顾问设备配置记录
        """
        try:
            async with self.database.get_session() as db_session:
                # 先通过device_id查找记录
                query = select(AdvisorDeviceConfig).where(
                    AdvisorDeviceConfig.device_id == device_id
                )
                result = await db_session.execute(query)
                device_config = result.scalar_one_or_none()

                if device_config:
                    # 如果存在，检查devid是否一致
                    if device_config.devid != devid:
                        # 不一致则同步devid
                        device_config.devid = devid
                        await db_session.commit()
                        logger.info("同步devid成功: device_id=%s, devid=%s", device_id, devid)
                    else:
                        logger.info("通过device_id获取设备配置成功: device_id=%s, advisor_id=%s", device_id, device_config.advisor_id)
                else:
                    # 如果不存在，创建新的advisor记录
                    # 首先获取下一个可用的advisor_id
                    max_advisor_query = select(func.max(Advisors.id))
                    max_result = await db_session.execute(max_advisor_query)
                    max_advisor_id = max_result.scalar() or 0
                    new_advisor_id = max_advisor_id + 1

                    # 先创建advisors记录
                    advisor = Advisors(
                        id=new_advisor_id,
                        group_id=2,  # 默认组ID
                        sub_group_id=None,
                        name=f"测试用户（{devid[:8]}）",  # 使用devid的前8位作为用户名
                        status=1  # 在职状态
                    )

                    db_session.add(advisor)
                    await db_session.flush()  # 刷新但不提交，确保advisor记录存在

                    # 创建新的设备配置记录
                    device_config = AdvisorDeviceConfig(
                        device_id=device_id,
                        devid=devid,
                        advisor_id=new_advisor_id,
                        advisor_name=f"测试用户（{devid[:8]}）",  # 使用devid的前8位作为用户名
                        goal=7200
                    )

                    db_session.add(device_config)
                    await db_session.commit()
                    await db_session.refresh(device_config)

                    logger.info("创建新的顾问和设备配置成功: device_id=%s, devid=%s, advisor_id=%s",
                              device_id, devid, new_advisor_id)

                return device_config

        except Exception as e:
            logger.error("获取或创建顾问设备配置失败: device_id=%s, devid=%s, 错误: %s", device_id, devid, str(e))
            raise
