
from typing import Annotated
from fastapi import APIRouter, Depends, Form

from app.core.dependencies import get_file_service
from app.schemas.base import BaseResponse
from app.schemas.file_record import FileUploadRequest
from app.services.upload_record_service import FileService
from app.models.events import EventType
# 创建路由器
router = APIRouter()

@router.post("/upload")
async def upload_audio( data: Annotated[FileUploadRequest, Form()], file_service: FileService = Depends(get_file_service)):
    """
    上传文件
    需要传入唯一的UUID作为file_uuid参数
    """
    try:
        data : BaseResponse = await file_service.emit_event(EventType.FILE_UPLOAD_RECORD, data=data, wait_for_result=True)
    except Exception as e:
        return BaseResponse.error(code=500, msg=f"Failed to upload file: {e}")
    finally:
        return data


