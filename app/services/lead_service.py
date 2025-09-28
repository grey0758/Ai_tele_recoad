"""
线索服务层

提供线索相关的业务逻辑处理
"""

from typing import Optional, Sequence
from sqlalchemy import select, and_, or_, text
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

                if query_params.category_id:
                    conditions.append(Lead.category_id == query_params.category_id)

                if query_params.advisor_id:
                    conditions.append(Lead.advisor_id == query_params.advisor_id)

                if query_params.customer_phone:
                    conditions.append(
                        Lead.customer_phone.like(f"%{query_params.customer_phone}%")
                    )

                if query_params.call_status_id:
                    conditions.append(
                        Lead.call_status_id == query_params.call_status_id
                    )

                if query_params.wechat_status_id:
                    conditions.append(
                        Lead.wechat_status_id == query_params.wechat_status_id
                    )

                if query_params.created_at_start:
                    conditions.append(Lead.created_at >= query_params.created_at_start)

                if query_params.created_at_end:
                    conditions.append(Lead.created_at <= query_params.created_at_end)

                # 搜索关键词
                if query_params.search:
                    search_conditions = or_(
                        Lead.customer_name.like(f"%{query_params.search}%"),
                        Lead.customer_phone.like(f"%{query_params.search}%"),
                        Lead.lead_no.like(f"%{query_params.search}%"),
                    )
                    conditions.append(search_conditions)

                # 构建查询
                query = select(Lead)
                if conditions:
                    query = query.where(and_(*conditions))

                # 获取总数
                count_query = select(text("COUNT(*)"))  # pylint: disable=not-callable
                if conditions:
                    count_query = count_query.where(and_(*conditions))

                total_result = await db_session.execute(count_query)
                scalar_value = total_result.scalar()
                total: int = scalar_value if scalar_value is not None else 0

                # 分页查询
                offset = (query_params.page - 1) * query_params.size
                query = query.offset(offset).limit(query_params.size)
                query = query.order_by(Lead.created_at.desc())

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
                # 检查线索编号是否已存在
                existing_lead = await self._get_lead_by_lead_no_with_session(
                    db_session, lead_data.lead_no
                )
                if existing_lead:
                    raise ValueError(f"线索编号 {lead_data.lead_no} 已存在")

                # 创建新线索
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

                # 如果更新线索编号，检查是否重复
                if lead_data.lead_no and lead_data.lead_no != lead.lead_no:
                    existing_lead = await self._get_lead_by_lead_no_with_session(
                        db_session, lead_data.lead_no
                    )
                    if existing_lead:
                        raise ValueError(f"线索编号 {lead_data.lead_no} 已存在")

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

    async def get_leads_by_status(
        self,
        call_status_id: Optional[int] = None,
        wechat_status_id: Optional[int] = None,
        schedule_status_id: Optional[int] = None,
        contract_status_id: Optional[int] = None,
        limit: int = 10,
    ) -> Sequence[Lead]:
        """根据状态获取线索列表"""
        async with self.database.get_session() as db_session:
            try:
                conditions = []

                if call_status_id is not None:
                    conditions.append(Lead.call_status_id == call_status_id)
                if wechat_status_id is not None:
                    conditions.append(Lead.wechat_status_id == wechat_status_id)
                if schedule_status_id is not None:
                    conditions.append(Lead.schedule_status_id == schedule_status_id)
                if contract_status_id is not None:
                    conditions.append(Lead.contract_status_id == contract_status_id)

                query = select(Lead)
                if conditions:
                    query = query.where(and_(*conditions))

                query = query.order_by(Lead.created_at.desc()).limit(limit)

                result = await db_session.execute(query)
                return result.scalars().all()

            except Exception as e:  # pylint: disable=broad-except
                logger.error("根据状态获取线索失败: %s", e)
                return []

    # 私有辅助方法，避免重复代码
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
                query = text("""
                    SELECT 
                        status_type,
                        type_name,
                        value,
                        code,
                        label,
                        parent_id,
                        sort_order
                    FROM v_frontend_status_mapping
                    ORDER BY status_type, parent_id IS NOT NULL, sort_order
                """)

                result = await db_session.execute(query)
                rows = result.fetchall()

                return [
                    {
                        "status_type": row.status_type,
                        "type_name": row.type_name,
                        "value": row.value,
                        "code": row.code,
                        "label": row.label,
                        "parent_id": row.parent_id,
                        "sort_order": row.sort_order
                    }
                    for row in rows
                ]

            except Exception as e:
                logger.error("获取状态映射失败: %s", e)
                raise
