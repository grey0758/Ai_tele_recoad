"""
线索服务层

提供线索相关的业务逻辑处理
"""
import json
from typing import Optional, Sequence

from sqlalchemy import select, and_, or_, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.event_bus import ProductionEventBus
from app.db.database import Database
from app.services.base_service import BaseService
from app.models.lead import Lead
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadQueryParams,
    LeadListResponse,
    LeadResponse,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


class LeadService(BaseService):
    """线索服务类"""

    def __init__(self, event_bus: ProductionEventBus, database: Database):
        super().__init__(event_bus=event_bus, service_name="LeadService")
        self.database = database  # 存储 database 对象

    async def initialize(self) -> bool:
        return True

    async def get_lead_by_id(self, lead_id: int) -> Optional[Lead]:
        """根据ID获取线索"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(Lead).where(Lead.id == lead_id)
                )
                return result.scalar_one_or_none()
            except Exception as e:  # pylint: disable=broad-except
                logger.error("获取线索失败: %s", e)
                return None

    async def get_lead_by_lead_no(self, lead_no: str) -> Optional[Lead]:
        """根据线索编号获取线索"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(Lead).where(Lead.lead_no == lead_no)
                )
                return result.scalar_one_or_none()
            except Exception as e:  # pylint: disable=broad-except
                logger.error("根据线索编号获取线索失败: %s", e)
                return None

    async def get_leads_with_pagination(
        self, query_params: LeadQueryParams
    ) -> LeadListResponse:
        """分页获取线索列表"""
        async with self.database.get_session() as db_session:
            try:
                # 构建查询条件
                conditions = []

                # 基础分类信息
                if query_params.category_id:
                    conditions.append(Lead.category_id == query_params.category_id)
                if query_params.sub_category_id:
                    conditions.append(Lead.sub_category_id == query_params.sub_category_id)

                # 分配信息
                if query_params.advisor_group_id:
                    conditions.append(Lead.advisor_group_id == query_params.advisor_group_id)
                if query_params.advisor_group_sub_id:
                    conditions.append(Lead.advisor_group_sub_id == query_params.advisor_group_sub_id)
                if query_params.advisor_id:
                    conditions.append(Lead.advisor_id == query_params.advisor_id)

                # 客户基础信息
                if query_params.customer_id:
                    conditions.append(Lead.customer_id == query_params.customer_id)
                if query_params.customer_name:
                    conditions.append(Lead.customer_name.like(f"%{query_params.customer_name}%"))
                if query_params.customer_phone:
                    conditions.append(Lead.customer_phone.like(f"%{query_params.customer_phone}%"))
                if query_params.customer_email:
                    conditions.append(Lead.customer_email.like(f"%{query_params.customer_email}%"))
                if query_params.customer_wechat_name:
                    conditions.append(Lead.customer_wechat_name.like(f"%{query_params.customer_wechat_name}%"))
                if query_params.customer_wechat_number:
                    conditions.append(Lead.customer_wechat_number.like(f"%{query_params.customer_wechat_number}%"))

                # 电话状态（主状态+子状态）
                if query_params.call_status_id:
                    conditions.append(Lead.call_status_id == query_params.call_status_id)
                if query_params.call_sub_status_id:
                    conditions.append(Lead.call_sub_status_id == query_params.call_sub_status_id)

                # 微信状态（主状态+子状态）
                if query_params.wechat_status_id:
                    conditions.append(Lead.wechat_status_id == query_params.wechat_status_id)
                if query_params.wechat_sub_status_id:
                    conditions.append(Lead.wechat_sub_status_id == query_params.wechat_sub_status_id)

                # 私域回看状态（主状态+子状态）
                if query_params.private_domain_review_status_id:
                    conditions.append(Lead.private_domain_review_status_id == query_params.private_domain_review_status_id)
                if query_params.private_domain_review_sub_status_id:
                    conditions.append(Lead.private_domain_review_sub_status_id == query_params.private_domain_review_sub_status_id)

                # 私域参加状态（主状态+子状态）
                if query_params.private_domain_participation_status_id:
                    conditions.append(Lead.private_domain_participation_status_id == query_params.private_domain_participation_status_id)
                if query_params.private_domain_participation_sub_status_id:
                    conditions.append(Lead.private_domain_participation_sub_status_id == query_params.private_domain_participation_sub_status_id)

                # 日程状态（主状态+子状态）
                if query_params.schedule_status_id:
                    conditions.append(Lead.schedule_status_id == query_params.schedule_status_id)
                if query_params.schedule_sub_status_id:
                    conditions.append(Lead.schedule_sub_status_id == query_params.schedule_sub_status_id)
                if query_params.schedule_times is not None:
                    conditions.append(Lead.schedule_times == query_params.schedule_times)

                # 合同状态（主状态+子状态）
                if query_params.contract_status_id:
                    conditions.append(Lead.contract_status_id == query_params.contract_status_id)
                if query_params.contract_sub_status_id:
                    conditions.append(Lead.contract_sub_status_id == query_params.contract_sub_status_id)

                # 分析字段
                if query_params.analysis_failed_records is not None:
                    conditions.append(Lead.analysis_failed_records == query_params.analysis_failed_records)
                if query_params.last_contact_record_id:
                    conditions.append(Lead.last_contact_record_id == query_params.last_contact_record_id)
                if query_params.last_contact_time_start:
                    conditions.append(Lead.last_contact_time >= query_params.last_contact_time_start)
                if query_params.last_contact_time_end:
                    conditions.append(Lead.last_contact_time <= query_params.last_contact_time_end)
                if query_params.last_analysis_failed_record_id:
                    conditions.append(Lead.last_analysis_failed_record_id == query_params.last_analysis_failed_record_id)
                if query_params.last_analysis_failed_time_start:
                    conditions.append(Lead.last_analysis_failed_time >= query_params.last_analysis_failed_time_start)
                if query_params.last_analysis_failed_time_end:
                    conditions.append(Lead.last_analysis_failed_time <= query_params.last_analysis_failed_time_end)

                # 时间范围查询
                if query_params.created_at_start:
                    conditions.append(Lead.created_at >= query_params.created_at_start)
                if query_params.created_at_end:
                    conditions.append(Lead.created_at <= query_params.created_at_end)
                if query_params.updated_at_start:
                    conditions.append(Lead.updated_at >= query_params.updated_at_start)
                if query_params.updated_at_end:
                    conditions.append(Lead.updated_at <= query_params.updated_at_end)

                # 搜索关键词
                if query_params.search:
                    search_conditions = or_(
                        Lead.customer_name.like(f"%{query_params.search}%"),
                        Lead.customer_phone.like(f"%{query_params.search}%"),
                        Lead.lead_no.like(f"%{query_params.search}%"),
                        Lead.customer_wechat_name.like(f"%{query_params.search}%"),
                        Lead.customer_wechat_number.like(f"%{query_params.search}%"),
                    )
                    conditions.append(search_conditions)

                # 构建查询
                query = select(Lead)
                if conditions:
                    query = query.where(and_(*conditions))

                # 获取总数
                count_query = select(func.count()).select_from(Lead) # pylint: disable=not-callable
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
                    sort_field = getattr(Lead, query_params.sort_field)
                except AttributeError:
                    sort_field = Lead.created_at

                if query_params.sort_order == "asc":
                    query = query.order_by(sort_field.asc())
                else:
                    query = query.order_by(sort_field.desc())

                result = await db_session.execute(query)
                leads: Sequence[Lead] = result.scalars().all()

                # 计算总页数
                pages = (total + query_params.size - 1) // query_params.size

                return LeadListResponse(
                    items=[LeadResponse.model_validate(lead) for lead in leads],
                    total=total,
                    page=query_params.page,
                    size=query_params.size,
                    pages=pages,
                )

            except Exception as e:  # pylint: disable=broad-except
                logger.error("分页获取线索列表失败: %s", e)
                raise

    async def create_lead(self, lead_data: LeadCreate) -> Lead:
        """创建线索"""
        async with self.database.get_session() as db_session:
            try:
                lead = Lead(**lead_data.model_dump())
                db_session.add(lead)
                await db_session.commit()
                await db_session.refresh(lead)

                logger.info("成功创建线索: %s", lead.lead_no)
                return lead

            except Exception as e:
                await db_session.rollback()
                logger.error("创建线索失败: %s", e)
                raise

    async def update_lead(self, lead_id: int, lead_data: LeadUpdate) -> Optional[Lead]:
        """更新线索"""
        async with self.database.get_session() as db_session:
            try:
                lead = await self._get_lead_by_id_with_session(db_session, lead_id)
                if not lead:
                    return None

                # 更新字段
                update_data = lead_data.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(lead, field, value)

                await db_session.commit()
                await db_session.refresh(lead)

                logger.info("成功更新线索: %s", lead.lead_no)
                return lead

            except Exception as e:
                await db_session.rollback()
                logger.error("更新线索失败: %s", e)
                raise

    async def delete_lead(self, lead_id: int) -> bool:
        """删除线索"""
        async with self.database.get_session() as db_session:
            try:
                lead = await self._get_lead_by_id_with_session(db_session, lead_id)
                if not lead:
                    return False

                await db_session.delete(lead)
                await db_session.commit()

                logger.info("成功删除线索: %s", lead.lead_no)
                return True

            except Exception as e:
                await db_session.rollback()
                logger.error("删除线索失败: %s", e)
                raise

    async def get_leads_by_advisor(
        self, advisor_id: int, limit: int = 10
    ) -> Sequence[Lead]:
        """根据顾问ID获取线索列表"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(Lead)
                    .where(Lead.advisor_id == advisor_id)
                    .order_by(Lead.created_at.desc())
                    .limit(limit)
                )
                return result.scalars().all()
            except Exception as e:  # pylint: disable=broad-except
                logger.error("根据顾问ID获取线索失败: %s", e)
                return []

    async def get_leads_by_category(
        self, category_id: int, limit: int = 10
    ) -> Sequence[Lead]:
        """根据分类ID获取线索列表"""
        async with self.database.get_session() as db_session:
            try:
                result = await db_session.execute(
                    select(Lead)
                    .where(Lead.category_id == category_id)
                    .order_by(Lead.created_at.desc())
                    .limit(limit)
                )
                return result.scalars().all()
            except Exception as e:  # pylint: disable=broad-except
                logger.error("根据分类ID获取线索失败: %s", e)
                return []

    async def _get_lead_by_id_with_session(
        self, db_session: AsyncSession, lead_id: int
    ) -> Optional[Lead]:
        """在指定会话中根据ID获取线索"""
        result = await db_session.execute(select(Lead).where(Lead.id == lead_id))
        return result.scalar_one_or_none()

    async def _get_lead_by_lead_no_with_session(
        self, db_session: AsyncSession, lead_no: str
    ) -> Optional[Lead]:
        """在指定会话中根据线索编号获取线索"""
        result = await db_session.execute(select(Lead).where(Lead.lead_no == lead_no))
        return result.scalar_one_or_none()

    async def get_status_mapping(self) -> list:
        """获取状态映射配置"""
        async with self.database.get_session() as db_session:
            try:
                # 先检查视图是否存在，如果不存在则返回空列表
                check_view_query = text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.views 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'view_lead_status_mapping'
                """)

                view_check = await db_session.execute(check_view_query)
                view_exists = view_check.scalar()

                if not view_exists:
                    logger.warning("视图 view_lead_status_mapping 不存在，返回空列表")
                    return []

                query = text("""
                    SELECT 
                        status_type,
                        type_name,
                        JSON_ARRAYAGG(
                            JSON_OBJECT(
                                'status_id', status_id,
                                'status_code', status_code,
                                'status_name', status_name,
                                'parent_id', parent_id,
                                'sort_order', sort_order,
                                'is_active', is_active
                            )
                        ) as status_list
                    FROM view_lead_status_mapping
                    GROUP BY status_type, type_name
                    ORDER BY status_type
                """)

                result = await db_session.execute(query)
                rows = result.fetchall()

                return [
                    {
                        "status_type": row.status_type,
                        "type_name": row.type_name,
                        "status_list": json.loads(row.status_list) if row.status_list else []
                    }
                    for row in rows
                ]

            except Exception as e:  # pylint: disable=broad-except
                logger.error("获取状态映射失败: %s", e)
                return []
