"""
通话记录服务层

提供通话记录相关的业务逻辑处理
"""
import json
import time
import uuid
from typing import Optional, Sequence
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.event_bus import ProductionEventBus
from app.db.database import Database
from app.services.base_service import BaseService
from app.services.redis_service import RedisService
from app.models.call_record_upload import CallRecordUpload
from app.models.advisor_call_duration_stats import AdvisorDeviceConfig
from app.models.advisors import Advisors
from app.models.lead import Lead
from app.schemas.call_record import (
    CallRecordCreate,
    CallRecordUpdate,
    CallRecordQueryParams,
    CallRecordListResponse,
    CallRecordResponse,
    CallTypeEnum,
)
from app.schemas.file_record import CallRecordUploadRequest
from app.models.events import EventType, EventPriority
from app.core.logger import get_logger
from app.utils.ai_judge_is_need2 import ai_analyze_call_quality

logger = get_logger(__name__)


class CallRecordsService(BaseService):
    """通话记录服务类"""
    def __init__(self, event_bus: ProductionEventBus, database: Database, redis_service: RedisService):
        super().__init__(event_bus=event_bus, service_name="CallRecordsService")
        self.database = database
        self.redis_service = redis_service

    async def initialize(self) -> bool:
        return True

    async def register_event_listeners(self):
        """注册事件监听器"""
        await self._register_listener(
            EventType.CALL_RECORDS_SAVE_AUTO_UPLOAD,
            self.handle_save_auto_upload,
            priority=EventPriority.HIGH
        )

    async def get_call_record_by_id(self, record_id: int) -> Optional[CallRecordUpload]:
        """根据ID获取通话记录"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(CallRecordUpload).where(CallRecordUpload.id == record_id)
                )
                return result.scalar_one_or_none()
            except Exception as e:  # pylint: disable=broad-except
                logger.error("获取通话记录失败: %s", e)
                return None

    async def get_call_record_by_uuid(self, record_uuid: str) -> Optional[CallRecordUpload]:
        """根据UUID获取通话记录"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(CallRecordUpload).where(CallRecordUpload.record_uuid == record_uuid)
                )
                return result.scalar_one_or_none()
            except Exception as e:  # pylint: disable=broad-except
                logger.error("根据UUID获取通话记录失败: %s", e)
                return None

    async def get_conversation_content(self, call_id: str) -> str:
        """获取通话的对话内容"""
        try:
            return await self.redis_service.get_conversation_content(call_id)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("获取对话内容失败: %s", e)
            return ""

    async def analyze_call_with_ai(self, conversation_content: str) -> tuple[int | None, str | None]:
        """使用AI分析通话质量和生成总结"""
        try:
            if not conversation_content or conversation_content.strip() == "":
                return None, None

            # 调用AI分析工具
            ai_result = ai_analyze_call_quality(conversation_content)

            # 解析JSON结果
            try:
                result_data = json.loads(ai_result)
                call_quality_score = result_data.get("call_quality_score")
                call_summary = result_data.get("call_summary")

                logger.info("AI分析完成 | score=%s, summary_length=%s",
                           call_quality_score, len(call_summary) if call_summary else 0)

                return call_quality_score, call_summary

            except json.JSONDecodeError as e:
                logger.error("AI分析结果JSON解析失败: %s", e)
                return None, None

        except Exception as e:  # pylint: disable=broad-except
            logger.error("AI分析通话失败: %s", e)
            return None, None

    async def get_call_records_with_pagination(
        self, query_params: CallRecordQueryParams
    ) -> CallRecordListResponse:
        """分页获取通话记录列表"""
        async with self.database.get_session() as db_session:
            try:
                # 构建查询条件
                conditions = []

                # 基础查询条件
                if query_params.dev_id:
                    conditions.append(CallRecordUpload.dev_id == query_params.dev_id)
                if query_params.record_id:
                    conditions.append(CallRecordUpload.record_id == query_params.record_id)
                if query_params.phone:
                    conditions.append(CallRecordUpload.phone.like(f"%{query_params.phone}%"))
                if query_params.call_type:
                    conditions.append(CallRecordUpload.call_type == query_params.call_type)
                if query_params.upload_state is not None:
                    conditions.append(CallRecordUpload.upload_state == query_params.upload_state)
                if query_params.cloud_uploaded is not None:
                    conditions.append(CallRecordUpload.cloud_uploaded == query_params.cloud_uploaded)

                # 业务查询条件
                if query_params.lead_id:
                    conditions.append(CallRecordUpload.lead_id == query_params.lead_id)
                if query_params.advisor_id:
                    conditions.append(CallRecordUpload.advisor_id == query_params.advisor_id)
                if query_params.advisor_group_id:
                    conditions.append(CallRecordUpload.advisor_group_id == query_params.advisor_group_id)

                # 时间范围查询
                if query_params.begin_time_start:
                    conditions.append(CallRecordUpload.begin_time >= query_params.begin_time_start)
                if query_params.begin_time_end:
                    conditions.append(CallRecordUpload.begin_time <= query_params.begin_time_end)
                if query_params.created_at_start:
                    conditions.append(CallRecordUpload.created_at >= query_params.created_at_start)
                if query_params.created_at_end:
                    conditions.append(CallRecordUpload.created_at <= query_params.created_at_end)

                # 构建查询
                query = select(CallRecordUpload)
                if conditions:
                    query = query.where(and_(*conditions))

                # 获取总数
                count_query = select(func.count()).select_from(CallRecordUpload) # pylint: disable=not-callable
                if conditions:
                    count_query = count_query.where(and_(*conditions))

                total_result = await db_session.execute(count_query)
                scalar_value = total_result.scalar()
                total: int = scalar_value if scalar_value is not None else 0

                # 分页查询
                offset = (query_params.page - 1) * query_params.size
                query = query.offset(offset).limit(query_params.size)

                # 动态排序
                try:
                    sort_field = getattr(CallRecordUpload, query_params.sort_field)
                except AttributeError:
                    sort_field = CallRecordUpload.created_at

                if query_params.sort_order == "asc":
                    query = query.order_by(sort_field.asc())
                else:
                    query = query.order_by(sort_field.desc())

                result = await db_session.execute(query)
                call_records: Sequence[CallRecordUpload] = result.scalars().all()

                # 计算总页数
                pages = (total + query_params.size - 1) // query_params.size

                return CallRecordListResponse(
                    items=[CallRecordResponse.model_validate(record) for record in call_records],
                    total=total,
                    page=query_params.page,
                    size=query_params.size,
                    pages=pages,
                )

            except Exception as e:  # pylint: disable=broad-except
                logger.error("分页获取通话记录列表失败: %s", e)
                raise

    async def create_call_record(self, record_data: CallRecordCreate) -> CallRecordUpload:
        """创建通话记录"""
        async with self.database.get_session() as db_session:
            try:
                call_record = CallRecordUpload(**record_data.model_dump())
                db_session.add(call_record)
                await db_session.commit()
                await db_session.refresh(call_record)

                logger.info("成功创建通话记录: %s", call_record.record_uuid)
                return call_record

            except Exception as e:  # pylint: disable=broad-except
                await db_session.rollback()
                logger.error("创建通话记录失败: %s", e)
                raise

    async def update_call_record(self, record_id: int, record_data: CallRecordUpdate) -> Optional[CallRecordUpload]:
        """更新通话记录"""
        async with self.database.get_session() as db_session:
            try:
                call_record = await self._get_call_record_by_id_with_session(db_session, record_id)
                if not call_record:
                    return None

                # 更新字段
                update_data = record_data.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(call_record, field, value)

                await db_session.commit()
                await db_session.refresh(call_record)

                logger.info("成功更新通话记录: %s", call_record.record_uuid)
                return call_record

            except Exception as e:  # pylint: disable=broad-except
                await db_session.rollback()
                logger.error("更新通话记录失败: %s", e)
                raise

    async def delete_call_record(self, record_id: int) -> bool:
        """删除通话记录"""
        async with self.database.get_session() as db_session:
            try:
                call_record = await self._get_call_record_by_id_with_session(db_session, record_id)
                if not call_record:
                    return False

                await db_session.delete(call_record)
                await db_session.commit()

                logger.info("成功删除通话记录: %s", call_record.record_uuid)
                return True

            except Exception as e:  # pylint: disable=broad-except
                await db_session.rollback()
                logger.error("删除通话记录失败: %s", e)
                raise

    async def get_call_records_by_device(
        self, dev_id: str, limit: int = 10
    ) -> Sequence[CallRecordUpload]:
        """根据设备ID获取通话记录列表"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(CallRecordUpload)
                    .where(CallRecordUpload.dev_id == dev_id)
                    .order_by(CallRecordUpload.created_at.desc())
                    .limit(limit)
                )
                return result.scalars().all()
            except Exception as e:  # pylint: disable=broad-except
                logger.error("根据设备ID获取通话记录失败: %s", e)
                return []

    async def get_call_records_by_advisor(
        self, advisor_id: int, limit: int = 10
    ) -> Sequence[CallRecordUpload]:
        """根据顾问ID获取通话记录列表"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(CallRecordUpload)
                    .where(CallRecordUpload.advisor_id == advisor_id)
                    .order_by(CallRecordUpload.created_at.desc())
                    .limit(limit)
                )
                return result.scalars().all()
            except Exception as e:  # pylint: disable=broad-except
                logger.error("根据顾问ID获取通话记录失败: %s", e)
                return []

    async def update_cloud_upload_status(
        self, record_id: int, cloud_url: str, uploaded: bool = True
    ) -> bool:
        """更新云存储上传状态"""
        async with self.database.get_session() as db_session:
            try:
                call_record = await self._get_call_record_by_id_with_session(db_session, record_id)
                if not call_record:
                    return False

                call_record.cloud_url = cloud_url
                call_record.cloud_uploaded = uploaded

                await db_session.commit()
                logger.info("成功更新云存储状态: %s", call_record.record_uuid)
                return True

            except Exception as e:  # pylint: disable=broad-except
                await db_session.rollback()
                logger.error("更新云存储状态失败: %s", e)
                raise

    async def _get_call_record_by_id_with_session(
        self, db_session: AsyncSession, record_id: int
    ) -> Optional[CallRecordUpload]:
        """在指定会话中根据ID获取通话记录"""
        result = await db_session.execute(select(CallRecordUpload).where(CallRecordUpload.id == record_id))
        return result.scalar_one_or_none()

    async def _get_call_record_by_uuid_with_session(
        self, db_session: AsyncSession, record_uuid: str
    ) -> Optional[CallRecordUpload]:
        """在指定会话中根据UUID获取通话记录"""
        result = await db_session.execute(select(CallRecordUpload).where(CallRecordUpload.record_uuid == record_uuid))
        return result.scalar_one_or_none()

    async def get_advisor_info_by_device_id(self, dev_id: str) -> Optional[dict]:
        """根据设备ID获取顾问信息"""
        async with self.database.get_session() as db_session:
            try:
                # 查询 advisor_device_config 表获取 advisor_id
                config_result = await db_session.execute(
                    select(AdvisorDeviceConfig.advisor_id, AdvisorDeviceConfig.advisor_name)
                    .where(AdvisorDeviceConfig.devid == dev_id)
                )
                config_row = config_result.first()

                if not config_row:
                    logger.warning("未找到设备ID对应的顾问配置: %s", dev_id)
                    return None

                advisor_id = config_row.advisor_id
                advisor_name = config_row.advisor_name

                # 查询 advisors 表获取顾问详细信息
                advisor_result = await db_session.execute(
                    select(Advisors.group_id, Advisors.sub_group_id, Advisors.status)
                    .where(Advisors.id == advisor_id)
                )
                advisor_row = advisor_result.first()

                if not advisor_row:
                    logger.warning("未找到顾问ID对应的顾问信息: %s", advisor_id)
                    return None

                return {
                    "advisor_id": advisor_id,
                    "advisor_name": advisor_name,
                    "advisor_group_id": advisor_row.group_id,
                    "advisor_group_sub_id": advisor_row.sub_group_id,
                    "advisor_status": advisor_row.status
                }

            except Exception as e:  # pylint: disable=broad-except
                logger.error("根据设备ID获取顾问信息失败: %s", e)
                return None

    async def create_lead_by_phone_and_group(self, phone: str, advisor_group_id: int, advisor_id: int, advisor_group_sub_id: Optional[int] = None) -> Optional[int]:
        """根据电话号码和顾问组创建线索"""
        async with self.database.get_session() as db_session:
            try:
                # 检查是否已存在相同电话号码的线索
                existing_lead = await db_session.execute(
                    select(Lead).where(Lead.customer_phone == phone)
                )
                lead = existing_lead.scalar_one_or_none()

                if lead:
                    logger.info("线索已存在，返回现有线索ID: %s", lead.id)
                    return lead.id

                # 根据 group_id 确定 category_id
                category_id = 3 if advisor_group_id == 2 else 4

                # 创建新线索
                new_lead = Lead(
                    category_id=category_id,
                    advisor_group_id=advisor_group_id,
                    advisor_group_sub_id=advisor_group_sub_id,
                    advisor_id=advisor_id,
                    customer_phone=phone
                )
                db_session.add(new_lead)
                await db_session.commit()
                await db_session.refresh(new_lead)

                logger.info("成功创建新线索: lead_id=%s", new_lead.id)
                return new_lead.id

            except Exception as e:  # pylint: disable=broad-except
                await db_session.rollback()
                logger.error("创建线索失败: %s", e)
                return None

    async def handle_save_auto_upload(self, event) -> dict:
        """处理自动上传保存事件"""
        try:
            # 从事件数据中获取CallRecordUploadRequest
            upload_request: CallRecordUploadRequest = event.data["upload_request"]
            upload_url: str | None = event.data["upload_url"]

            call_record_data = await self._convert_upload_request_to_model(upload_request)
            if upload_url:
                call_record_data.cloud_url = upload_url
                call_record_data.cloud_uploaded = True

            call_record = await self.create_call_record(call_record_data)

            logger.info("成功处理自动上传保存事件: %s", call_record.record_uuid)

            return {
                "success": True,
                "record_id": call_record.id,
                "record_uuid": call_record.record_uuid,
                "message": "通话记录保存成功"
            }

        except Exception as e:  # pylint: disable=broad-except
            logger.error("处理自动上传保存事件失败: %s", e)
            return {
                "success": False,
                "error": str(e),
                "message": "通话记录保存失败"
            }

    async def _convert_upload_request_to_model(self, upload_request: CallRecordUploadRequest) -> CallRecordCreate:
        """将CallRecordUploadRequest转换为CallRecordCreate模型"""

        # 从CallRecordUploadRequest中提取数据
        record = upload_request.record

        call_no = upload_request.record.uuid if upload_request.record.uuid and upload_request.record.uuid.strip() else f"CALL{int(time.time())}{str(uuid.uuid4())[:8]}"

        # 根据文件处理逻辑设置本地路径
        local_path = f"uploads/{record.FileName}" if upload_request.HasFile == 1 else None

        # 获取对话内容并进行AI分析
        if record.uuid:
            conversation_content = await self.get_conversation_content(record.uuid)
        else:
            conversation_content = ""

        if conversation_content:
            call_quality_score, call_summary = await self.analyze_call_with_ai(conversation_content)
        else:
            call_quality_score = None
            call_summary = None

        # 根据设备ID获取顾问信息
        advisor_info = await self.get_advisor_info_by_device_id(record.DevId)

        # 初始化业务字段
        advisor_id = None
        advisor_group_id = None
        advisor_group_sub_id = None
        lead_id = None

        if advisor_info:
            advisor_id = advisor_info.get("advisor_id")
            advisor_group_id = advisor_info.get("advisor_group_id")
            advisor_group_sub_id = advisor_info.get("advisor_group_sub_id")
            logger.info("成功获取顾问信息 | dev_id=%s, advisor_id=%s, advisor_group_id=%s", record.DevId, advisor_id, advisor_group_id)

            # 根据电话号码和顾问组创建线索
            if record.Phone and advisor_group_id and advisor_id:
                lead_id = await self.create_lead_by_phone_and_group(
                    phone=record.Phone,
                    advisor_group_id=advisor_group_id,
                    advisor_id=advisor_id,
                    advisor_group_sub_id=advisor_group_sub_id if advisor_group_sub_id else None
                )
                if lead_id:
                    logger.info("成功创建或获取线索 | phone=%s, lead_id=%s", record.Phone, lead_id)
        else:
            logger.warning("未找到设备ID对应的顾问信息: %s", record.DevId)

        return CallRecordCreate(
            # 基础字段 - 直接从CallRecord中读取
            dev_id=record.DevId,
            record_id=record.Id,
            ch=record.Ch,
            begin_time=record.BeginTime,
            end_time=record.EndTime,
            time_len=record.TimeLen,
            call_type=CallTypeEnum(record.Type.value),
            phone=record.Phone,
            dtmf_keys=record.DtmfKeys,
            ring_count=record.RingCount,
            file_size=record.FileSize,
            file_name=record.FileName,
            custom_id=record.CustomId,
            record_uuid=record.uuid if record.uuid and record.uuid.strip() else str(uuid.uuid4()),
            upload_state=record.UploadState,

            # 存储信息
            local_path=local_path,
            cloud_url=None,
            cloud_uploaded=False,

            # 业务扩展字段
            call_no=call_no,
            lead_id=lead_id,
            advisor_id=advisor_id,
            advisor_group_id=advisor_group_id,
            advisor_group_sub_id=advisor_group_sub_id,
            conversation_content=conversation_content,
            call_summary=call_summary,
            call_quality_score=call_quality_score,
            quality_notes=None
        )
