"""
顾问通话时长统计 API 端点

提供顾问通话时长统计相关的 REST API 接口
"""

from typing import List
from datetime import date
from fastapi import APIRouter, Depends, Query, Path

from app.services.aiBox_service import AiBoxService
from app.schemas.advisor_call_duration_stats import (
    AdvisorCallDurationStatsUpsertRequest,
    AdvisorCallDurationStatsResponse,
)
from app.models.events import EventType
from app.schemas.base import ResponseData, ResponseBuilder, ResponseCode
from app.core.dependencies import get_aibox_service
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/advisor-call-duration-stats",
    response_model=ResponseData[AdvisorCallDurationStatsResponse],
    summary="更新或插入顾问通话时长统计",
)
async def upsert_advisor_call_duration_stats(
    stats_data: AdvisorCallDurationStatsUpsertRequest,
    aibox_service: AiBoxService = Depends(get_aibox_service),
):
    """
    更新或插入顾问通话时长统计

    如果 UNIQUE KEY (advisor_id, stats_date) 存在则更新，否则插入新记录
    """
    try:
        stats = await aibox_service.upsert_advisor_call_duration_stats(stats_data)
        response_data = AdvisorCallDurationStatsResponse.model_validate(stats)
        return ResponseBuilder.success(response_data, "更新或插入顾问通话时长统计成功")

    except Exception as e:
        logger.error("更新或插入顾问通话时长统计失败: %s", e)
        return ResponseBuilder.error(
            f"更新或插入顾问通话时长统计失败: {str(e)}", ResponseCode.INTERNAL_ERROR
        )


@router.get(
    "/advisor-call-duration-stats/{advisor_id}/{stats_date}",
    response_model=ResponseData[AdvisorCallDurationStatsResponse],
    summary="获取顾问通话时长统计",
)
async def get_advisor_call_duration_stats(
    advisor_id: int = Path(..., description="顾问ID"),
    stats_date: date = Path(..., description="统计日期"),
    aibox_service: AiBoxService = Depends(get_aibox_service),
):
    """
    根据顾问ID和统计日期获取通话时长统计
    """
    try:
        stats = await aibox_service.get_advisor_call_duration_stats(
            advisor_id, stats_date
        )
        if not stats:
            return ResponseBuilder.not_found("未找到指定的顾问通话时长统计记录")

        response_data = AdvisorCallDurationStatsResponse.model_validate(stats)
        return ResponseBuilder.success(response_data, "获取顾问通话时长统计成功")

    except Exception as e:
        logger.error("获取顾问通话时长统计失败: %s", e)
        return ResponseBuilder.error(
            f"获取顾问通话时长统计失败: {str(e)}", ResponseCode.INTERNAL_ERROR
        )


@router.get(
    "/advisor-call-duration-stats/{advisor_id}/range",
    response_model=ResponseData[List[AdvisorCallDurationStatsResponse]],
    summary="获取顾问通话时长统计范围",
)
async def get_advisor_call_duration_stats_range(
    advisor_id: int = Path(..., description="顾问ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    aibox_service: AiBoxService = Depends(get_aibox_service),
):
    """
    根据顾问ID和日期范围获取通话时长统计列表
    """
    try:
        stats_list = await aibox_service.get_advisor_stats_by_date_range(
            advisor_id, start_date, end_date
        )
        response_data = [
            AdvisorCallDurationStatsResponse.model_validate(stats)
            for stats in stats_list
        ]
        return ResponseBuilder.success(response_data, "获取顾问通话时长统计范围成功")

    except Exception as e:
        logger.error("获取顾问通话时长统计范围失败: %s", e)
        return ResponseBuilder.error(
            f"获取顾问通话时长统计范围失败: {str(e)}", ResponseCode.INTERNAL_ERROR
        )


@router.get(
    "/advisor-call-duration-stats/by-date",
    response_model=ResponseData[List[AdvisorCallDurationStatsResponse]],
    summary="获取指定日期所有顾问通话时长统计",
)
async def get_all_advisor_call_duration_stats_by_date(
    stats_date: date = Query(
        default_factory=date.today, description="统计日期（默认今天）"
    ),
    aibox_service: AiBoxService = Depends(get_aibox_service),
):
    """
    获取指定日期的所有顾问通话时长统计
    """
    try:
        stats_list = await aibox_service.get_all_advisor_stats_by_date(stats_date)
        response_data = [
            AdvisorCallDurationStatsResponse.model_validate(stats)
            for stats in stats_list
        ]
        return ResponseBuilder.success(
            response_data, "获取指定日期所有顾问通话时长统计成功"
        )

    except Exception as e:
        logger.error("获取指定日期所有顾问通话时长统计失败: %s", e)
        return ResponseBuilder.error(
            f"获取指定日期所有顾问通话时长统计失败: {str(e)}",
            ResponseCode.INTERNAL_ERROR,
        )


@router.get(
    "/advisor-call-duration-stats/trigger-wechat-report",
    response_model=ResponseData[dict],
    summary="手动触发顾问时长统计微信播报任务",
)
async def trigger_advisor_stats_wechat_report(
    aibox_service: AiBoxService = Depends(get_aibox_service),
):
    """
    手动触发顾问时长统计微信播报任务
    
    不需要任何输入参数，直接调用即可触发微信播报任务
    """
    try:
        success = await aibox_service.emit_event(EventType.SEND_ADVISOR_STATS_WECHAT_REPORT_TASK, data=None, wait_for_result=True)
        if success:
            return ResponseBuilder.success(
                {"triggered": True, "message": "顾问时长统计微信播报任务已触发"}, 
                "手动触发顾问时长统计微信播报任务成功"
            )
        else:
            return ResponseBuilder.error(
                "手动触发顾问时长统计微信播报任务失败", 
                ResponseCode.INTERNAL_ERROR
            )

    except Exception as e:  # pylint: disable=broad-except
        logger.error("手动触发顾问时长统计微信播报任务失败: %s", e)
        return ResponseBuilder.error(
            f"手动触发顾问时长统计微信播报任务失败: {str(e)}", 
            ResponseCode.INTERNAL_ERROR
        )
