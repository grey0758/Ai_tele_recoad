"""
API 路由配置

配置所有 API 路由
"""

from fastapi import APIRouter
from app.api.v1.endpoints.upload_record import router as file_router
from app.api.v1.endpoints.lead import router as lead_router

api_router = APIRouter()

api_router.include_router(file_router, tags=["UploadRecord"])
api_router.include_router(lead_router, tags=["Lead"])
