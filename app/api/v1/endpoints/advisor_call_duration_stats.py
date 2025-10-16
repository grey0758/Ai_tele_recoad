"""
顾问通话时长统计 API 端点

提供顾问通话时长统计相关的 REST API 接口
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Path

from app.services.aibox_service import Aiboxservice
from app.schemas.advisor_call_duration_stats import (
    AdvisorCallDurationStatsUpdateRequestWithDeviceIdAndStatsDate,
    AdvisorCallDurationStatsResponse,
    AdvisorDeviceConfigResponse,
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
    stats_data: AdvisorCallDurationStatsUpdateRequestWithDeviceIdAndStatsDate,
    aibox_service: Aiboxservice = Depends(get_aibox_service),
):
    """
    更新或插入顾问通话时长统计

    如果 UNIQUE KEY (advisor_id, stats_date) 存在则更新，否则插入新记录
    如果total_duration小于等于0，直接返回成功，不进行数据库更新
    """
    try:
        # 检查total_duration是否小于等于0
        if not stats_data.total_duration or stats_data.total_duration <= 0:
            logger.info("通话时长为0或负数，跳过数据库更新: device_id=%s, total_duration=%d", 
                       stats_data.device_id, stats_data.total_duration)
            return ResponseBuilder.success(None, "无通话时长，跳过更新")
        
        stats = await aibox_service.upsert_advisor_call_duration_stats(stats_data)
        response_data = AdvisorCallDurationStatsResponse.model_validate(stats)
        return ResponseBuilder.success(response_data, "更新或插入顾问通话时长统计成功")

    except Exception as e:  # pylint: disable=broad-except
        logger.error("更新或插入顾问通话时长统计失败: %s", e)
        raise HTTPException(status_code=ResponseCode.INTERNAL_ERROR, detail=f"更新或插入顾问通话时长统计失败: {str(e)}") from e


@router.get(
    "/advisor-call-duration-stats/{advisor_id}/{stats_date}",
    response_model=ResponseData[AdvisorCallDurationStatsResponse],
    summary="获取顾问通话时长统计",
)
async def get_advisor_call_duration_stats(
    advisor_id: int = Path(..., description="顾问ID"),
    stats_date: date = Path(..., description="统计日期"),
    aibox_service: Aiboxservice = Depends(get_aibox_service),
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

    except Exception as e:  # pylint: disable=broad-except
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
    aibox_service: Aiboxservice = Depends(get_aibox_service),
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

    except Exception as e:  # pylint: disable=broad-except
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
    aibox_service: Aiboxservice = Depends(get_aibox_service),
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

    except Exception as e:  # pylint: disable=broad-except
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
    aibox_service: Aiboxservice = Depends(get_aibox_service),
):
    """
    手动触发顾问时长统计微信播报任务

    不需要任何输入参数，直接调用即可触发微信播报任务
    """
    #返回str
    message = await aibox_service.emit_event(
            EventType.SEND_ADVISOR_STATS_WECHAT_REPORT_TASK,
            data=None,
            wait_for_result=True,
            max_retries=0,
        )
    return ResponseBuilder.success(None, message)


@router.post(
    "/generate-advisor-analysis-report",
    response_model=ResponseData[dict],
    summary="手动触发顾问分析报告生成任务",
)
async def trigger_generate_advisor_analysis_report(
    target_date: Optional[str] = None,
    aibox_service: Aiboxservice = Depends(get_aibox_service),
):
    """
    手动触发顾问分析报告生成任务

    Args:
        target_date: 目标日期，格式为 YYYY-MM-DD，默认为今天
    """
    try:
        # 准备事件数据
        event_data = {}
        if target_date:
            event_data["target_date"] = target_date
        
        # 触发事件
        message = await aibox_service.emit_event(
            EventType.GENERATE_ADVISOR_ANALYSIS_REPORT_TASK,
            data=event_data if event_data else None,
            wait_for_result=True,
            max_retries=0,
        )
        
        return ResponseBuilder.success({"message": message}, "顾问分析报告生成任务已触发")
        
    except Exception as e:
        logger.error("触发顾问分析报告生成任务失败: %s", e)
        return ResponseBuilder.error(f"触发任务失败: {str(e)}", ResponseCode.INTERNAL_ERROR)


@router.get(
    "/advisor-device-config/by-device-id/{device_id}",
    response_model=ResponseData[AdvisorDeviceConfigResponse],
    summary="通过设备ID获取或创建顾问设备配置",
)
async def get_or_create_advisor_device_config(
    device_id: str = Path(..., description="设备ID"),
    devid: str = Query(..., description="设备ID（新字段）"),
    aibox_service: Aiboxservice = Depends(get_aibox_service),
):
    """
    通过设备ID获取或创建顾问设备配置
    
    1. 通过device_id查找记录
    2. 如果存在，验证devid是否一致，不一致则同步
    3. 如果不存在，则创建新的advisor记录
    """
    try:
        device_config = await aibox_service.get_or_create_advisor_device_config(device_id, devid)
        response_data = AdvisorDeviceConfigResponse.model_validate(device_config)
        return ResponseBuilder.success(response_data, "获取或创建顾问设备配置成功")

    except Exception as e:  # pylint: disable=broad-except
        logger.error("获取或创建顾问设备配置失败: device_id=%s, devid=%s, 错误: %s", device_id, devid, str(e))
        return ResponseBuilder.error(
            f"获取或创建顾问设备配置失败: {str(e)}", ResponseCode.INTERNAL_ERROR
        )
