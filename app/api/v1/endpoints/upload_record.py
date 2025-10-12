"""
文件上传 API 端点

提供文件上传相关的 REST API 接口
"""

from typing import Annotated
from fastapi import APIRouter, Depends, Form, File, UploadFile, Query
from app.schemas.file_record import CallRecord, CallRecordsRequest
from app.core.dependencies import get_file_service
from app.schemas.base import ResponseData, ResponseBuilder, ResponseCode
from app.schemas.file_record import FileUploadRequest, CallSystemResponse
from app.services.upload_record_service import FileService
from app.services.cloud_service import CloudService
from app.models.events import EventType
from app.core.logger import get_logger
from app.services.call_records_service import CallRecordsService
from app.core.dependencies import get_call_records_service


# 创建路由器
router = APIRouter()

# 获取日志记录器
logger = get_logger(__name__)


@router.post("/upload", response_model=ResponseData[dict])
async def upload_audio(
    data: Annotated[FileUploadRequest, Form()],
    file_service: FileService = Depends(get_file_service),
):
    """
    上传文件
    需要传入唯一的UUID作为file_uuid参数
    """
    try:
        result = await file_service.emit_event(EventType.FILE_UPLOAD_RECORD, data=data, wait_for_result=True)
        return ResponseBuilder.success(result, "文件上传成功")
    except Exception as e:  # pylint: disable=broad-except
        return ResponseBuilder.error(f"文件上传失败: {str(e)}", ResponseCode.INTERNAL_ERROR)

@router.post("/upload-af-crm", response_model=CallSystemResponse, response_model_exclude_none=True)
async def upload_af_crm(
    cmd: str = Query(default="UpLoadRecord"),
    record: str = Form(default=""),
    fileName: str = Form(default=""), # pylint: disable=invalid-name
    HasFile: int = Form(default=0), # pylint: disable=invalid-name
    file: UploadFile = File(default=None),
    call_records_service: CallRecordsService = Depends(get_call_records_service),
):
    """
    CallSystem上传录音接口
    """
    logger.info("接收到参数: cmd=%s, fileName=%s, HasFile=%s", cmd, fileName, HasFile)
    logger.info("record数据长度: %d", len(record))
    recoard : CallRecord = CallRecord.model_validate_json(record)
    # 创建上传请求对象（用于验证数据完整性）
    upload_request = CallRecordsRequest(
        record=recoard,
        fileName=fileName,
        HasFile=HasFile,
        file=file
    )

    # 保存文件到本地和云存储
    if file and file.filename:
        try:
            # 读取文件内容
            content = await file.read()
            logger.info("📁 文件大小: %d 字节", len(content))

            # # 1. 保存到本地uploads文件夹
            # upload_dir = "uploads"
            # os.makedirs(upload_dir, exist_ok=True)
            # local_path = os.path.join(upload_dir, file.filename)
            # with open(local_path, "wb") as f:
            #     f.write(content)
            # logger.info("✅ 本地文件保存成功: %s", local_path)

            # 2. 上传到云存储
            try:
                # 创建云存储服务实例并上传到COS
                cloud_service_instance = CloudService()
                upload_result = await cloud_service_instance.upload_file(
                    file_content=content,
                    filename=file.filename,
                    path=f"call-records/{recoard.Id}",
                    content_type='audio/mpeg'  # MP3文件类型
                )

                if upload_result.success:
                    logger.info("✅ 云存储上传成功: %s", upload_result.url)
                    await call_records_service.emit_event(EventType.CALL_RECORDS_SAVE_AUTO_UPLOAD, data={ "upload_request": upload_request, "upload_url": upload_result.url })
                    return CallSystemResponse(
                        Code=0,
                        errMsg="文件上传成功",
                        NextUploadId=recoard.Id + 1
                    )
                else:
                    logger.error("❌ 云存储上传失败: %s", upload_result.error)
                    return CallSystemResponse(
                        Code=-1,
                        errMsg=f"云存储上传失败: {upload_result.error}",
                        NextUploadId=None
                    )

            except Exception as cloud_error: # pylint: disable=broad-except
                logger.error("❌ 云存储服务异常: %s", cloud_error)
                # 即使云存储失败，本地保存成功也算部分成功
                return CallSystemResponse(
                    Code=0,
                    errMsg="本地保存成功，云存储失败",
                    NextUploadId=recoard.Id + 1
                )

        except Exception as e: # pylint: disable=broad-except
            logger.error("❌ 文件处理失败: %s", e)
            return CallSystemResponse(
                Code=-1,
                errMsg=f"文件处理失败: {str(e)}",
                NextUploadId=None
            )
    else:
        logger.warning("✅ 没有文件需要保存")
        await call_records_service.emit_event(EventType.CALL_RECORDS_SAVE_AUTO_UPLOAD, data={ "upload_request": upload_request, "upload_url": None })
        return CallSystemResponse(
            Code=0,
            errMsg="没有文件需要保存",
            NextUploadId=None
        )
