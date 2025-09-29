"""
线索 API 端点

提供线索相关的 REST API 接口
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Path

from app.services.lead_service import LeadService
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadListResponse,
    LeadQueryParams,
    StatusMappingResponse,
)
from app.core.dependencies import get_lead_service
from app.core.logger import get_logger
from app.schemas.base import ResponseCode, ResponseBuilder, ResponseData

logger = get_logger(__name__)

router = APIRouter()


@router.post("/lead/search", response_model=ResponseData[LeadListResponse], summary="搜索线索列表")
async def search_leads(
    query_params: LeadQueryParams,
    lead_service: LeadService = Depends(get_lead_service),
):
    """
    搜索线索列表

    支持全面的查询条件：
    - 基础分类信息：线索类型、子类型
    - 分配信息：顾问组、顾问
    - 客户基础信息：姓名、电话、邮箱、微信等
    - 状态查询：电话、微信、私域、日程、合同状态（主状态+子状态）
    - 分析字段：联系次数、时间范围等
    - 时间范围查询：创建时间、更新时间
    - 关键词搜索：客户姓名、电话、线索编号、微信昵称、微信号码
    - 动态排序：支持按任意字段排序
    """
    try:
        result = await lead_service.get_leads_with_pagination(query_params)
        return ResponseBuilder.success(result)

    except Exception as e:
        logger.error("搜索线索列表失败: %s", e)
        raise HTTPException(status_code=ResponseCode.INTERNAL_ERROR, detail=f"搜索线索列表失败: {str(e)}") from e


@router.get("/lead/status-mapping", summary="获取状态映射配置", response_model=ResponseData[List[StatusMappingResponse]])
async def get_status_mapping(
    lead_service: LeadService = Depends(get_lead_service)
):
    """
    获取所有状态映射配置
    
    返回所有状态类型的映射关系，包括：
    - 电话状态
    - 微信状态  
    - 私域回看状态
    - 私域参加状态
    - 日程状态
    - 合同状态
    """
    try:
        result = await lead_service.get_status_mapping()
        return ResponseBuilder.success(result)
    except Exception as e:
        logger.error("获取状态映射失败: %s", e)
        raise HTTPException(status_code=500, detail=f"获取状态映射失败: {str(e)}") from e


@router.get("/lead/{lead_id}", response_model= ResponseData[LeadResponse], summary="根据ID获取线索")
async def get_lead_by_id(lead_id: int = Path(..., description="线索ID"), lead_service: LeadService = Depends(get_lead_service)):
    """
    根据ID获取线索详情
    """
    try:
        lead = await lead_service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="线索不存在")

        return ResponseBuilder.success(LeadResponse.model_validate(lead))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取线索详情失败: %s", e)
        raise HTTPException(status_code=500, detail=f"获取线索详情失败: {str(e)}") from e


@router.get("/lead/lead-no/{lead_no}", response_model=LeadResponse, summary="根据线索编号获取线索",)
async def get_lead_by_lead_no(lead_no: str = Path(..., description="线索编号"), lead_service: LeadService = Depends(get_lead_service)):
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


@router.post("/lead", response_model=LeadResponse, summary="创建线索")
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


@router.put("/lead/{lead_id}", response_model=LeadResponse, summary="更新线索")
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


@router.delete("lead/{lead_id}", summary="删除线索")
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


@router.get("/lead/advisor/{advisor_id}", response_model=List[LeadResponse], summary="根据顾问ID获取线索",)
async def get_leads_by_advisor(advisor_id: int = Path(..., description="顾问ID"), limit: int = Query(10, ge=1, le=100, description="返回数量限制"), lead_service: LeadService = Depends(get_lead_service)):
    """
    根据顾问ID获取线索列表
    """
    try:
        leads = await lead_service.get_leads_by_advisor(advisor_id, limit)
        return [LeadResponse.model_validate(lead) for lead in leads]

    except Exception as e:
        logger.error("根据顾问ID获取线索失败: %s", e)
        raise HTTPException(status_code=500, detail=f"根据顾问ID获取线索失败: {str(e)}") from e


@router.get("/lead/category/{category_id}", response_model=List[LeadResponse], summary="根据分类ID获取线索",)
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
