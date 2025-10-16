"""
aiBox 服务层

提供顾问通话时长统计相关的业务逻辑处理
"""

import os
from typing import Optional, Dict, Any
from datetime import date, datetime
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
from app.models.advisor_analysis_report import AdvisorAnalysisReport
from app.schemas.advisor_call_duration_stats import (
    AdvisorCallDurationStatsUpdateRequestWithDeviceIdAndStatsDate,
)
from app.schemas.advisor_analysis_report import AdvisorAnalysisReportCreate, AdvisorAnalysisReportUpdate
from app.models.events import EventPriority
from app.core.logger import get_logger
from app.services.cloud_service import CloudService
from app.utils.advisor_recording_report import analyze_consultant_data, save_consultant_analysis
from app.services.call_records_service import CallRecordsService

logger = get_logger(__name__)


class Aiboxservice(BaseService):
    """aiox 服务类"""

    def __init__(self, event_bus: ProductionEventBus, database: Database, call_records_service: Optional[CallRecordsService] = None):
        super().__init__(event_bus=event_bus, service_name="AiBoxService")
        self.database = database
        self.call_records_service = call_records_service
        self.event_bus = event_bus
        self.cloud_service = CloudService()

    async def initialize(self) -> bool:
        return True

    async def register_event_listeners(self):
        """注册事件监听器"""
        await self._register_listener(EventType.SEND_ADVISOR_STATS_WECHAT_REPORT_TASK, self.send_advisor_stats_wechat_report_task, priority=EventPriority.HIGH, timeout=30.0)
        await self._register_listener(EventType.GENERATE_ADVISOR_ANALYSIS_REPORT_TASK, self.generate_advisor_analysis_report, priority=EventPriority.HIGH, timeout=1000.0)

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
        self, stats_date: date = date.today(), advisor_group_id: int = 1
    ) -> list[AdvisorCallDurationStats]:
        """获取指定日期的所有顾问通话时长统计"""
        async with self.database.get_session() as db_session:
            try:
                # 先获取指定顾问组的所有顾问ID
                advisor_ids_result = await db_session.execute(
                    select(Advisors.id)
                    .where(Advisors.group_id == advisor_group_id)
                )
                advisor_ids = [row[0] for row in advisor_ids_result.fetchall()]
                
                if not advisor_ids:
                    logger.warning("顾问组 %d 中没有找到任何顾问", advisor_group_id)
                    return []
                
                # 根据顾问ID列表获取统计数据
                result = await db_session.execute(
                    select(AdvisorCallDurationStats)
                    .where(
                        and_(
                            AdvisorCallDurationStats.stats_date == stats_date,
                            AdvisorCallDurationStats.advisor_id.in_(advisor_ids)
                        )
                    )
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

        # 通过事件发送微信消息，不等待结果
        await self.emit_event(
            EventType.SEND_WECHAT_MESSAGE,
            data={
                "to_wxid": "58065692621@chatroom",
                "msg": {"text": msg, "xml": "", "url": "", "name": "", "url_thumb": ""},
                "to_ren": "",
                "msg_type": 1,
                "send_type": 1,
            },
            wait_for_result=False
        )

        return "微信播报事件已发送"

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

    async def generate_advisor_analysis_report(
        self, 
        _: Event | None = None,
        target_date: Optional[date] = None
    ) -> Dict[int, str]:
        """
        生成所有顾问的分析报告
        
        Args:
            target_date: 目标日期，默认为今天
            
        Returns:
            Dict[int, str]: 顾问ID到报告文件路径的映射
        """
        if target_date is None:
            target_date = date.today()
            
        if not self.call_records_service:
            logger.error("通话记录服务实例未提供")
            return {}
            
        try:
            # 1. 先获取有通话记录的顾问ID列表
            advisor_records = await self.call_records_service.get_daily_advisor_call_records(
                target_date=target_date,
                advisor_group_id=1,  # 使用默认组ID，让服务返回所有组的记录
                limit_per_advisor=10,  # 获取前十条
                enable_transcription=True,
                max_concurrent_transcription=5
            )
            
            if not advisor_records:
                logger.warning("未找到任何顾问的通话记录")
                return {}
            
            # 2. 针对有通话记录的顾问，获取统计数据并生成报告
            results = {}
            for advisor_id, records in advisor_records.items():
                if not records:
                    logger.warning("顾问 %s 没有通话记录", advisor_id)
                    continue
                    
                # 获取统计数据
                stats = await self.get_advisor_call_duration_stats(advisor_id, target_date)
                if not stats:
                    logger.warning("未找到顾问 %s 在 %s 的统计数据", advisor_id, target_date)
                    continue
                
                # 构建顾问数据格式
                adviser_data: Dict[str, Any] = {
                    "total_calls": stats.total_calls,
                    "calls": []
                }
                
                for record in records:
                    call_data = {
                        "record_id": record.id,
                        "customer_id": record.lead_id,
                        "phone": record.phone,
                        "call_time": datetime.fromtimestamp(record.begin_time).strftime("%Y-%m-%d %H:%M:%S"),
                        "duration_seconds": record.time_len,
                        "file_url": record.cloud_url,
                        "remark": record.quality_notes or "",
                        "transcript": record.conversation_content or ""
                    }
                    adviser_data["calls"].append(call_data)
                
                # 构建日度量化指标
                daily_metrics = {
                    "call_count": stats.total_calls,
                    "connected_calls": stats.total_connected,
                    "connection_rate": f"{float(stats.connection_rate):.1f}%",
                    "effective_calls": stats.total_connected,  # 假设接通的都是有效通话
                    "effective_call_rate": f"{float(stats.connection_rate):.1f}%",
                    "average_effective_duration": f"{int(stats.total_duration / stats.total_connected // 60)}分{int(stats.total_duration / stats.total_connected % 60)}秒" if stats.total_connected > 0 else "0分0秒", # pylint: disable=line-too-long
                    "total_effective_duration_minutes": f"{stats.total_duration/60:.1f}"
                }
                
                # 调用分析函数
                analysis_content, error = analyze_consultant_data(
                    consultant_name=stats.advisor_name,
                    report_date=target_date.strftime("%Y-%m-%d"),
                    adviser_data=adviser_data,
                    daily_metrics=daily_metrics
                )
                
                if error:
                    logger.error("分析顾问 %s 数据失败: %s", advisor_id, error)
                    continue
                    
                # 保存分析报告
                report_path = save_consultant_analysis(
                    consultant_name=stats.advisor_name,
                    analysis_content=analysis_content,
                    report_date=target_date.strftime("%Y-%m-%d")
                )
                
                if report_path:
                    cloud_url = await self._upload_report_to_cloud_and_save_record(
                        advisor_id=advisor_id,
                        advisor_name=stats.advisor_name,
                        report_date=target_date,
                        local_file_path=report_path,
                        report_content=analysis_content,
                        daily_metrics=daily_metrics
                    )
                    
                    if cloud_url:
                        results[advisor_id] = cloud_url
                        logger.info("成功生成并上传顾问 %s 分析报告: %s", advisor_id, cloud_url)
                    else:
                        results[advisor_id] = report_path
                        logger.warning("顾问 %s 报告生成成功但上传失败，保留本地文件: %s", advisor_id, report_path)
                else:
                    logger.error("顾问 %s 报告生成失败", advisor_id)
            
            logger.info("完成所有顾问分析报告生成，成功: %d 个", len(results))
            return results
            
        except Exception as e:
            logger.error("生成顾问分析报告失败: %s", e)
            return {}

    async def _upload_report_to_cloud_and_save_record(
        self, 
        advisor_id: int, 
        advisor_name: str, 
        report_date: date, 
        local_file_path: str,
        report_content: str,
        daily_metrics: Dict[str, Any]
    ) -> Optional[str]:
        """
        上传报告到云存储并保存数据库记录
        
        Args:
            advisor_id: 顾问ID
            advisor_name: 顾问姓名
            report_date: 报告日期
            local_file_path: 本地文件路径
            report_content: 报告内容
            daily_metrics: 日度指标
            
        Returns:
            str: 云存储URL，失败时返回None
        """
        try:
            # 1. 上传到云存储
            cloud_path = f"advisor_reports/{report_date.strftime('%Y/%m/%d')}"
            
            upload_result = await self.cloud_service.upload_file_from_path(
                file_path=local_file_path,
                path=cloud_path
            )
            
            if not upload_result.success:
                logger.error("上传文件到云存储失败: %s", upload_result.error)
                return None
            
            # 2. 检查是否已存在今天的记录
            existing_report = await self._get_existing_report(advisor_id, report_date)

            data = {
                        "to_wxid": "wxid_demhpxriofpd22",
                        "msg": {
                            "text": "",
                            "xml": "",
                            "url": f"{upload_result.url}",
                            "name": f"{upload_result.object_key}",
                            "url_thumb": ""
                        },
                        "to_ren": "",
                        "msg_type": 6,
                        "send_type": 1
                    }
            
            await self.emit_event(EventType.SEND_WECHAT_MESSAGE,data=data,wait_for_result=False)
            
            if existing_report:
                # 更新现有记录
                update_data = AdvisorAnalysisReportUpdate(
                    cloud_url=upload_result.url,
                    cloud_object_key=upload_result.object_key,
                    is_uploaded=True,
                    is_deleted=False
                )
                success = await self._update_report_record(int(existing_report.id), update_data)
                if success:
                    logger.info("更新顾问 %s 的报告记录，云URL: %s", advisor_name, upload_result.url)
                else:
                    logger.error("更新顾问 %s 的报告记录失败", advisor_name)
            else:
                # 创建新记录
                report_data = AdvisorAnalysisReportCreate(
                    advisor_id=advisor_id,
                    advisor_name=advisor_name,
                    report_date=report_date,
                    report_type="daily",
                    local_file_path=local_file_path,
                    cloud_url=upload_result.url,
                    cloud_object_key=upload_result.object_key,
                    report_content=report_content,
                    report_summary=f"{advisor_name}的{report_date}日度分析报告",
                    total_calls=daily_metrics.get("call_count", 0),
                    connected_calls=daily_metrics.get("connected_calls", 0),
                    connection_rate=daily_metrics.get("connection_rate", "0%"),
                    effective_calls=daily_metrics.get("effective_calls", 0),
                    effective_call_rate=daily_metrics.get("effective_call_rate", "0%"),
                    total_duration_minutes=daily_metrics.get("total_effective_duration_minutes", "0"),
                    is_uploaded=True,
                    is_deleted=False
                )
                report = await self._create_report_record(report_data)
                if report:
                    logger.info("创建顾问 %s 的报告记录，云URL: %s", advisor_name, upload_result.url)
                else:
                    logger.error("创建顾问 %s 的报告记录失败", advisor_name)
            
            # 3. 删除本地文件
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                logger.info("已删除本地文件: %s", local_file_path)
            
            return upload_result.url
            
        except Exception as e:
            logger.error("处理报告上传和保存失败: %s", e)
            return None

    async def _get_existing_report(self, advisor_id: int, report_date: date) -> Optional[AdvisorAnalysisReport]:
        """获取现有的报告记录"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(AdvisorAnalysisReport).where(
                        and_(
                            AdvisorAnalysisReport.advisor_id == advisor_id,
                            AdvisorAnalysisReport.report_date == report_date
                        )
                    )
                )
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error("查询现有报告记录失败: %s", e)
                return None

    async def _create_report_record(self, report_data: AdvisorAnalysisReportCreate) -> Optional[AdvisorAnalysisReport]:
        """创建报告记录"""
        async with self.database.get_session() as db_session:
            try:
                report = AdvisorAnalysisReport(**report_data.model_dump())
                db_session.add(report)
                await db_session.commit()
                await db_session.refresh(report)
                return report
            except Exception as e:
                logger.error("创建报告记录失败: %s", e)
                await db_session.rollback()
                return None

    async def _update_report_record(self, report_id: int, update_data: AdvisorAnalysisReportUpdate) -> bool:
        """更新报告记录"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(AdvisorAnalysisReport).where(AdvisorAnalysisReport.id == report_id)
                )
                report = result.scalar_one_or_none()
                
                if not report:
                    logger.error("报告记录不存在: %s", report_id)
                    return False
                
                # 更新字段
                for field, value in update_data.model_dump(exclude_unset=True).items():
                    setattr(report, field, value)
                
                await db_session.commit()
                return True
            except Exception as e:
                logger.error("更新报告记录失败: %s", e)
                await db_session.rollback()
                return False
