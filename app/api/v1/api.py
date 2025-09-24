from fastapi import APIRouter
from app.api.v1.endpoints.upload_record import router as file_router

api_router = APIRouter()

api_router.include_router(file_router, tags=["UploadRecord"])




