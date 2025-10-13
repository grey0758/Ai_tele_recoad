"""
API 路由配置

配置所有 API 路由
"""

from fastapi import APIRouter
from app.api.v1.endpoints.upload_record import router as file_router
from app.api.v1.endpoints.lead import router as lead_router
from app.api.v1.endpoints.advisor_call_duration_stats import router as advisor_stats_router
from app.api.v1.endpoints.ai_advisor_stats import router as ai_advisor_stats_router
from app.api.v1.endpoints.scheduled_tasks import router as scheduled_tasks_router

api_router = APIRouter()

api_router.include_router(file_router, tags=["UploadRecord"])
api_router.include_router(lead_router, tags=["Lead"])
api_router.include_router(advisor_stats_router, tags=["AdvisorCallDurationStats"])
api_router.include_router(ai_advisor_stats_router, tags=["AiAdvisorStats"])
api_router.include_router(scheduled_tasks_router, tags=["ScheduledTasks"])
