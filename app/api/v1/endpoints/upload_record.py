
from typing import Annotated
from fastapi import APIRouter, Depends, Form

from app.core.dependencies import get_file_service
from app.schemas.base import ResponseData, ResponseBuilder, ResponseCode
from app.schemas.file_record import FileUploadRequest
from app.services.upload_record_service import FileService
from app.models.events import EventType
# 创建路由器
router = APIRouter()

@router.post("/upload", response_model=ResponseData[dict])
async def upload_audio( data: Annotated[FileUploadRequest, Form()], file_service: FileService = Depends(get_file_service)):
    """
    上传文件
    需要传入唯一的UUID作为file_uuid参数
    """
    try:
        result = await file_service.emit_event(EventType.FILE_UPLOAD_RECORD, data=data, wait_for_result=True)
        return ResponseBuilder.success(result, "文件上传成功")
    except Exception as e:
        return ResponseBuilder.error(f"文件上传失败: {str(e)}", ResponseCode.INTERNAL_ERROR)


