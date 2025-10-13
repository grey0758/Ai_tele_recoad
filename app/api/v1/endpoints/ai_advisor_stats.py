"""
AI顾问统计 API 端点

提供AI顾问统计相关的 REST API 接口
"""
from typing import Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, Query
from app.services.ai_tele_status_service import AiTeleStatusService
from app.models.events import EventType
from app.schemas.base import ResponseData, ResponseBuilder, ResponseCode
from app.core.dependencies import get_ai_tele_status_service
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/ai-advisor-merged-stats",
    response_model=ResponseData[Dict[str, Any]],
    summary="获取AI顾问合并统计数据",
    description="获取指定日期的所有AI顾问（group_id=2）合并统计数据"
)
async def get_ai_advisor_merged_stats(
    stats_date: date = Query(default=date.today(), description="统计日期"),
    ai_tele_status_service: AiTeleStatusService = Depends(get_ai_tele_status_service)
):
    """获取AI顾问合并统计数据"""
    try:
        merged_stats = await ai_tele_status_service.get_merged_ai_advisor_stats_by_date(stats_date)
        return ResponseBuilder.success(merged_stats, "获取AI顾问合并统计数据成功")
    except Exception as e:
        logger.error("获取AI顾问合并统计数据失败: %s", e)
        return ResponseBuilder.error(f"获取AI顾问合并统计数据失败: {str(e)}", ResponseCode.INTERNAL_ERROR)


@router.post(
    "/ai-advisor-wechat-report",
    response_model=ResponseData[str],
    summary="发送AI顾问统计微信播报",
    description="发送AI顾问统计数据的微信播报"
)
async def send_ai_advisor_wechat_report(
    ai_tele_status_service: AiTeleStatusService = Depends(get_ai_tele_status_service)
):
    """发送AI顾问统计微信播报"""
    try:
        # 通过事件发送AI顾问统计微信播报
        await ai_tele_status_service.emit_event(
            EventType.SEND_AI_ADVISOR_STATS_WECHAT_REPORT_TASK,
            wait_for_result=False
        )
        return ResponseBuilder.success("AI顾问统计微信播报事件已发送", "发送成功")
    except Exception as e:
        logger.error("发送AI顾问统计微信播报失败: %s", e)
        return ResponseBuilder.error(f"发送AI顾问统计微信播报失败: {str(e)}", ResponseCode.INTERNAL_ERROR)
