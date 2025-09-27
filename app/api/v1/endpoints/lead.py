"""
线索 API 端点

提供线索相关的 REST API 接口
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path

from app.services.lead_service import LeadService
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadListResponse,
    LeadQueryParams,
)
from app.core.dependencies import get_lead_service
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/leads", response_model=LeadListResponse, summary="获取线索列表")
async def get_leads(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(10, ge=1, le=100, description="每页数量，最大100"),
    category_id: Optional[int] = Query(None, description="线索类型ID"),
    advisor_id: Optional[int] = Query(None, description="顾问ID"),
    customer_phone: Optional[str] = Query(None, description="客户电话"),
    call_status_id: Optional[int] = Query(None, description="电话状态ID"),
    wechat_status_id: Optional[int] = Query(None, description="微信状态ID"),
    created_at_start: Optional[str] = Query(
        None, description="创建时间开始 (YYYY-MM-DD)"
    ),
    created_at_end: Optional[str] = Query(
        None, description="创建时间结束 (YYYY-MM-DD)"
    ),
    search: Optional[str] = Query(
        None, description="搜索关键词（客户姓名、电话、线索编号）"
    ),
    lead_service: LeadService = Depends(get_lead_service),
):
    """
    获取线索列表

    支持分页查询和多种筛选条件：
    - 按线索类型筛选
    - 按顾问筛选
    - 按客户电话筛选
    - 按状态筛选
    - 按创建时间范围筛选
    - 关键词搜索
    """
    try:
        # 处理日期时间参数
        created_at_start_dt = None
        created_at_end_dt = None

        if created_at_start:
            try:
                created_at_start_dt = datetime.fromisoformat(created_at_start)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail="创建时间开始格式错误，请使用 YYYY-MM-DD 格式",
                ) from e

        if created_at_end:
            try:
                created_at_end_dt = datetime.fromisoformat(created_at_end)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail="创建时间结束格式错误，请使用 YYYY-MM-DD 格式",
                ) from e

        # 构建查询参数
        query_params = LeadQueryParams(
            page=page,
            size=size,
            category_id=category_id,
            advisor_id=advisor_id,
            customer_phone=customer_phone,
            call_status_id=call_status_id,
            wechat_status_id=wechat_status_id,
            created_at_start=created_at_start_dt,
            created_at_end=created_at_end_dt,
            search=search,
        )

        result = await lead_service.get_leads_with_pagination(query_params)
        return result

    except Exception as e:
        logger.error("获取线索列表失败: %s", e)
        raise HTTPException(status_code=500, detail=f"获取线索列表失败: {str(e)}") from e


@router.get("/leads/{lead_id}", response_model=LeadResponse, summary="根据ID获取线索")
async def get_lead_by_id(
    lead_id: int = Path(..., description="线索ID"),
    lead_service: LeadService = Depends(get_lead_service),
):
    """
    根据ID获取线索详情
    """
    try:
        lead = await lead_service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="线索不存在")

        return LeadResponse.model_validate(lead)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取线索详情失败: %s", e)
        raise HTTPException(status_code=500, detail=f"获取线索详情失败: {str(e)}") from e


@router.get(
    "/leads/lead-no/{lead_no}",
    response_model=LeadResponse,
    summary="根据线索编号获取线索",
)
async def get_lead_by_lead_no(
    lead_no: str = Path(..., description="线索编号"),
    lead_service: LeadService = Depends(get_lead_service),
):
    """
    根据线索编号获取线索详情
    """
    try:
        lead = await lead_service.get_lead_by_lead_no(lead_no)
        if not lead:
            raise HTTPException(status_code=404, detail="线索不存在")

        return LeadResponse.model_validate(lead)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("根据线索编号获取线索失败: %s", e)
        raise HTTPException(
            status_code=500, detail=f"根据线索编号获取线索失败: {str(e)}"
        ) from e


@router.post("/leads", response_model=LeadResponse, summary="创建线索")
async def create_lead(
    lead_data: LeadCreate, lead_service: LeadService = Depends(get_lead_service)
):
    """
    创建新线索
    """
    try:
        lead = await lead_service.create_lead(lead_data)
        return LeadResponse.model_validate(lead)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("创建线索失败: %s", e)
        raise HTTPException(status_code=500, detail=f"创建线索失败: {str(e)}") from e


@router.put("/leads/{lead_id}", response_model=LeadResponse, summary="更新线索")
async def update_lead(
    lead_data: LeadUpdate,
    lead_id: int = Path(..., description="线索ID"),
    lead_service: LeadService = Depends(get_lead_service),
):
    """
    更新线索信息
    """
    try:
        lead = await lead_service.update_lead(lead_id, lead_data)
        if not lead:
            raise HTTPException(status_code=404, detail="线索不存在")

        return LeadResponse.model_validate(lead)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error("更新线索失败: %s", e)
        raise HTTPException(status_code=500, detail=f"更新线索失败: {str(e)}") from e


@router.delete("/leads/{lead_id}", summary="删除线索")
async def delete_lead(
    lead_id: int = Path(..., description="线索ID"),
    lead_service: LeadService = Depends(get_lead_service),
):
    """
    删除线索
    """
    try:
        success = await lead_service.delete_lead(lead_id)
        if not success:
            raise HTTPException(status_code=404, detail="线索不存在")

        return {"message": "线索删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("删除线索失败: %s", e)
        raise HTTPException(status_code=500, detail=f"删除线索失败: {str(e)}") from e


@router.get(
    "/leads/advisor/{advisor_id}",
    response_model=List[LeadResponse],
    summary="根据顾问ID获取线索",
)
async def get_leads_by_advisor(
    advisor_id: int = Path(..., description="顾问ID"),
    limit: int = Query(10, ge=1, le=100, description="返回数量限制"),
    lead_service: LeadService = Depends(get_lead_service),
):
    """
    根据顾问ID获取线索列表
    """
    try:
        leads = await lead_service.get_leads_by_advisor(advisor_id, limit)
        return [LeadResponse.model_validate(lead) for lead in leads]

    except Exception as e:
        logger.error("根据顾问ID获取线索失败: %s", e)
        raise HTTPException(status_code=500, detail=f"根据顾问ID获取线索失败: {str(e)}") from e


@router.get(
    "/leads/category/{category_id}",
    response_model=List[LeadResponse],
    summary="根据分类ID获取线索",
)
async def get_leads_by_category(
    category_id: int = Path(..., description="分类ID"),
    limit: int = Query(10, ge=1, le=100, description="返回数量限制"),
    lead_service: LeadService = Depends(get_lead_service),
):
    """
    根据分类ID获取线索列表
    """
    try:
        leads = await lead_service.get_leads_by_category(category_id, limit)
        return [LeadResponse.model_validate(lead) for lead in leads]

    except Exception as e:
        logger.error("根据分类ID获取线索失败: %s", e)
        raise HTTPException(status_code=500, detail=f"根据分类ID获取线索失败: {str(e)}") from e


@router.get(
    "/leads/status", response_model=List[LeadResponse], summary="根据状态获取线索"
)
async def get_leads_by_status(
    call_status_id: Optional[int] = Query(None, description="电话状态ID"),
    wechat_status_id: Optional[int] = Query(None, description="微信状态ID"),
    schedule_status_id: Optional[int] = Query(None, description="日程状态ID"),
    contract_status_id: Optional[int] = Query(None, description="合同状态ID"),
    limit: int = Query(10, ge=1, le=100, description="返回数量限制"),
    lead_service: LeadService = Depends(get_lead_service),
):
    """
    根据状态获取线索列表

    可以按一个或多个状态进行筛选
    """
    try:
        leads = await lead_service.get_leads_by_status(
            call_status_id=call_status_id,
            wechat_status_id=wechat_status_id,
            schedule_status_id=schedule_status_id,
            contract_status_id=contract_status_id,
            limit=limit,
        )
        return [LeadResponse.model_validate(lead) for lead in leads]

    except Exception as e:
        logger.error("根据状态获取线索失败: %s", e)
        raise HTTPException(status_code=500, detail=f"根据状态获取线索失败: {str(e)}") from e
