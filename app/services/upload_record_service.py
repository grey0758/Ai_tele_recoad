from pathlib import Path 
from app.core.config import settings
from app.core.logger import get_logger
from app.schemas.base import BaseResponse
from app.schemas.file_record import FileUploadRequest, FileUploadResponse
from app.services.base_service import BaseService
from app.core.event_bus import ProductionEventBus
from app.models.events import EventType, Event

logger = get_logger(__name__)

class FileService(BaseService):
    """文件服务类 - 处理实际的文件上传逻辑"""
    def __init__(self, event_bus: ProductionEventBus):
        super().__init__(event_bus=event_bus, service_name="FileService")

    async def initialize(self) -> bool:
        return True

    async def register_event_listeners(self):
        await self._register_listener(EventType.FILE_UPLOAD_RECORD, self.upload_file)
    
    async def upload_file(self, event: Event) -> BaseResponse:
        try:
            logger.info(f"Uploading file: {event.data}")

            if not isinstance(event.data, FileUploadRequest):
                raise TypeError("event.data 不是 FileUploadRequest 类型")
            request_data: FileUploadRequest = event.data

            # 确保上传目录存在
            upload_dir = Path(settings.upload_dir)
            upload_dir.mkdir(parents=True, exist_ok=True)  # 使用 pathlib 的 mkdir 方法

            # 生成文件名
            filename = f"{request_data.file_uuid}.mp3"

            # 构建文件路径并写入文件
            file_path = upload_dir / filename
            file_content = await request_data.file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)


            # 返回响应
            file_url = f"/uploads/{filename}"
            response_data = FileUploadResponse(file_url=f"http://localhost:8022{file_url}")
            return BaseResponse.success(response_data)
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return BaseResponse.error(code=500, msg=f"Failed to upload file: {e}")
