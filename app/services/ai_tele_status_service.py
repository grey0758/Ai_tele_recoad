"""
AI顾问统计服务层

提供AI顾问（group_id=2）通话时长统计相关的业务逻辑处理
"""

from datetime import date
from typing import Dict, Any
from sqlalchemy import select, and_, func
from app.core.event_bus import ProductionEventBus
from app.db.database import Database
from app.services.base_service import BaseService
from app.models.advisor_call_duration_stats import AdvisorCallDurationStats
from app.models.advisors import Advisors
from app.models.events import Event, EventType
from app.core.logger import get_logger

logger = get_logger(__name__)


class AiTeleStatusService(BaseService):
    """AI顾问统计服务类"""

    def __init__(self, event_bus: ProductionEventBus, database: Database):
        super().__init__(event_bus=event_bus, service_name="AiTeleStatusService")
        self.database = database
        self.event_bus = event_bus

    async def initialize(self) -> bool:
        return True

    async def register_event_listeners(self):
        """注册事件监听器"""
        await self._register_listener(EventType.SEND_AI_ADVISOR_STATS_WECHAT_REPORT_TASK, self.send_ai_advisor_stats_wechat_report_task)

    async def get_merged_ai_advisor_stats_by_date(
        self, stats_date: date = date.today()
    ) -> Dict[str, Any]:
        """
        合并所有AI顾问（group_id=2）的统计数据，生成一条agent顾问今日数据
        
        Args:
            stats_date: 统计日期，默认为今天
            
        Returns:
            Dict[str, Any]: 合并后的统计数据
        """
        async with self.database.get_session() as db_session:
            try:
                # 先获取group_id为2的所有顾问ID
                advisor_ids_result = await db_session.execute(
                    select(Advisors.id)
                    .where(Advisors.group_id == 2)
                )
                advisor_ids = [row[0] for row in advisor_ids_result.fetchall()]
                
                if not advisor_ids:
                    logger.warning("AI顾问组（group_id=2）中没有找到任何顾问")
                    return self._create_empty_merged_stats(stats_date)
                
                # 聚合所有AI顾问的统计数据
                result = await db_session.execute(
                    select(
                        func.sum(AdvisorCallDurationStats.total_calls).label('total_calls'),
                        func.sum(AdvisorCallDurationStats.total_connected).label('total_connected'),
                        func.sum(AdvisorCallDurationStats.total_duration).label('total_duration'),
                        func.sum(AdvisorCallDurationStats.duration_over_60s).label('duration_over_60s'),
                        func.sum(AdvisorCallDurationStats.duration_20s_to_30s).label('duration_20s_to_30s'),
                        func.count(AdvisorCallDurationStats.advisor_id).label('advisor_count') # pylint: disable=not-callable
                    )
                    .where(
                        and_(
                            AdvisorCallDurationStats.stats_date == stats_date,
                            AdvisorCallDurationStats.advisor_id.in_(advisor_ids)
                        )
                    )
                )
                
                row = result.first()
                if not row or row.total_calls is None:
                    logger.warning("未找到AI顾问在 %s 的统计数据", stats_date)
                    return self._create_empty_merged_stats(stats_date)
                
                # 计算接通率
                connection_rate = 0.0
                if row.total_calls > 0:
                    connection_rate = (row.total_connected / row.total_calls) * 100
                
                # 构建合并后的统计数据
                merged_stats = {
                    "顾问姓名": "AI顾问汇总",
                    "统计日期": stats_date,
                    "设备ID": "ai_agent_merged",
                    "总呼叫记录数": row.total_calls or 0,
                    "总接通数目": row.total_connected or 0,
                    "总通话时长(秒)": row.total_duration or 0,
                    "接通率(%)": round(connection_rate, 2),
                    "通话时长大于60秒总数": row.duration_over_60s or 0,
                    "通话时长20-30秒总数": row.duration_20s_to_30s or 0,
                    "参与统计顾问数": row.advisor_count or 0
                }
                
                logger.info(
                    "成功合并AI顾问统计数据: 日期=%s, 顾问数=%d, 总通话=%d, 接通=%d, 总时长=%d秒, 接通率=%.2f%%",
                    stats_date,
                    merged_stats["参与统计顾问数"],
                    merged_stats["总呼叫记录数"],
                    merged_stats["总接通数目"],
                    merged_stats["总通话时长(秒)"],
                    merged_stats["接通率(%)"]
                )
                
                return merged_stats
                
            except Exception as e:  # pylint: disable=broad-except
                logger.error("合并AI顾问统计数据失败: %s", e)
                return self._create_empty_merged_stats(stats_date)

    def _create_empty_merged_stats(self, stats_date: date) -> Dict[str, Any]:
        """创建空的合并统计数据"""
        return {
            "顾问姓名": "AI顾问汇总",
            "统计日期": stats_date,
            "设备ID": "ai_agent_merged",
            "总呼叫记录数": 0,
            "总接通数目": 0,
            "总通话时长(秒)": 0,
            "接通率(%)": 0.0,
            "通话时长大于60秒总数": 0,
            "通话时长20-30秒总数": 0,
            "参与统计顾问数": 0
        }

    async def send_ai_advisor_stats_wechat_report_task(self, _event: Event) -> str:
        """发送AI顾问统计微信播报定时任务"""
        try:
            # 获取合并的AI顾问统计数据
            merged_stats = await self.get_merged_ai_advisor_stats_by_date(date.today())
            
            # 生成微信播报消息
            msg_lines = ["=== AI顾问汇总统计 ==="]
            msg_lines.append(f"\n顾问姓名: {merged_stats['顾问姓名']}")
            msg_lines.append(f"统计日期: {merged_stats['统计日期']}")
            msg_lines.append(f"参与统计顾问数: {merged_stats['参与统计顾问数']}")
            msg_lines.append(f"总呼叫记录数: {merged_stats['总呼叫记录数']}")
            msg_lines.append(f"总接通数目: {merged_stats['总接通数目']}")
            msg_lines.append(f"总通话时长: {merged_stats['总通话时长(秒)']}秒")
            msg_lines.append(f"接通率: {merged_stats['接通率(%)']}%")
            msg_lines.append(f"通话时长大于60秒总数: {merged_stats['通话时长大于60秒总数']}")
            msg_lines.append(f"通话时长20-30秒总数: {merged_stats['通话时长20-30秒总数']}")
            
            msg = "\n".join(msg_lines)
            logger.info("生成的AI顾问微信播报消息:\n%s", msg)
            
            # 通过事件发送微信消息，不等待结果
            await self.emit_event(
                EventType.SEND_WECHAT_MESSAGE,
                data={
                    "to_wxid": "50251377407@chatroom",
                    "message": msg
                },
                wait_for_result=False
            )
            
            return "AI顾问微信播报事件已发送"
            
        except Exception as e:
            error_msg = f"发送AI顾问统计微信播报失败: {str(e)}"
            logger.error(error_msg)
            return error_msg
