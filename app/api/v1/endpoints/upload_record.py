"""
文件上传 API 端点

提供文件上传相关的 REST API 接口
"""

from typing import Annotated
import os
from fastapi import APIRouter, Depends, Form, File, UploadFile, Query
from app.schemas.file_record import CallRecord, CallRecordUploadRequest
from app.core.dependencies import get_file_service
from app.schemas.base import ResponseData, ResponseBuilder, ResponseCode
from app.schemas.file_record import FileUploadRequest, CallSystemResponse
from app.services.upload_record_service import FileService
from app.services.cloud_service import CloudService
from app.models.events import EventType


# 创建路由器
router = APIRouter()


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
    file: UploadFile = File(default=None)
):
    """
    CallSystem上传录音接口
    暂时返回错误状态用于测试接口连通性
    """
    # 暂时不处理任何参数，仅用于测试接口连通性,测试接口连通性
    print(f"接收到参数: cmd={cmd}, fileName={fileName}, HasFile={HasFile}")
    print(f"record数据长度: {len(record)}")
    recoard : CallRecord = CallRecord.model_validate_json(record)
    # 创建上传请求对象（用于验证数据完整性）
    _ = CallRecordUploadRequest(
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
            print(f"📁 文件大小: {len(content)} 字节")

            # 1. 保存到本地uploads文件夹
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            local_path = os.path.join(upload_dir, file.filename)
            with open(local_path, "wb") as f:
                f.write(content)
            print(f"✅ 本地文件保存成功: {local_path}")

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

                if upload_result['success']:
                    print(f"✅ 云存储上传成功: {upload_result['url']}")
                    return CallSystemResponse(
                        Code=0,
                        errMsg="文件上传成功",
                        NextUploadId=recoard.Id + 1
                    )
                else:
                    print(f"❌ 云存储上传失败: {upload_result['error']}")
                    return CallSystemResponse(
                        Code=-1,
                        errMsg=f"云存储上传失败: {upload_result['error']}",
                        NextUploadId=None
                    )

            except Exception as cloud_error: # pylint: disable=broad-except
                print(f"❌ 云存储服务异常: {cloud_error}")
                # 即使云存储失败，本地保存成功也算部分成功
                return CallSystemResponse(
                    Code=0,
                    errMsg="本地保存成功，云存储失败",
                    NextUploadId=recoard.Id + 1
                )

        except Exception as e: # pylint: disable=broad-except
            print(f"❌ 文件处理失败: {e}")
            return CallSystemResponse(
                Code=-1,
                errMsg=f"文件处理失败: {str(e)}",
                NextUploadId=None
            )
    else:
        print("❌ 没有文件需要保存")
        return CallSystemResponse(
            Code=-1,
            errMsg="没有文件需要保存",
            NextUploadId=None
        )
