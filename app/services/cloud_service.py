"""
腾讯云COS云存储服务
"""

import os
import logging
from qcloud_cos import CosConfig, CosS3Client  # type: ignore
from app.core.config import settings
from app.schemas.cloud_response import CloudUploadResponse, CloudDeleteResponse

logger = logging.getLogger(__name__)


class CloudService:
    """腾讯云COS云存储服务"""

    def __init__(self):
        """初始化COS客户端"""
        self.secret_id = settings.cos_secret_id
        self.secret_key = settings.cos_secret_key
        self.region = settings.cos_region
        self.bucket = settings.cos_bucket

        if not all([self.secret_id, self.secret_key, self.bucket]):
            raise ValueError(
                "缺少必要的COS配置: cos_secret_id, cos_secret_key, cos_bucket"
            )

        # 配置COS客户端
        config = CosConfig(
            Region=self.region, SecretId=self.secret_id, SecretKey=self.secret_key
        )
        self.client = CosS3Client(config)
        logger.info(
            "COS客户端初始化成功，区域: %s, 存储桶: %s",
            self.region,
            self.bucket,
        )

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        path: str | None = None,
        content_type: str | None = None,
    ) -> CloudUploadResponse:
        """
        统一文件上传接口

        Args:
            file_content: 文件内容（字节）
            filename: 文件名
            path: 云存储路径，如果为None则使用文件名
            content_type: 内容类型

        Returns:
            上传响应信息
        """
        try:
            # 构建对象键
            if path:
                object_key = f"{path}/{filename}"
            else:
                object_key = filename

            content_type = self._get_content_type(filename)

            response = self.client.put_object(
                Bucket=self.bucket,
                Body=file_content,
                Key=object_key,
                ContentType=content_type,
                ContentDisposition="inline"
            )

            logger.info("文件上传成功: %s, ETag: %s", object_key, response.get("ETag"))
            return CloudUploadResponse(
                success=True,
                object_key=object_key,
                filename=filename,
                etag=response.get("ETag"),
                url=await self.get_file_url(object_key) if response.get("ETag") else None
            )

        except Exception as e:  # pylint: disable=broad-except
            logger.error("文件上传失败: %s, 错误: %s", filename, str(e))
            return CloudUploadResponse(success=False, error=str(e))

    async def upload_file_from_path(
        self,
        file_path: str,
        path: str | None = None,
        content_type: str | None = None,
    ) -> CloudUploadResponse:
        """
        从本地文件路径上传到COS

        Args:
            file_path: 本地文件路径
            path: 云存储路径，如果为None则使用文件名
            content_type: 内容类型

        Returns:
            上传响应信息
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 获取文件名
            filename = os.path.basename(file_path)

            # 读取文件内容
            with open(file_path, "rb") as fp:
                file_content = fp.read()

            return await self.upload_file(file_content, filename, path, content_type)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("从路径上传文件失败: %s, 错误: %s", file_path, str(e))
            return CloudUploadResponse(success=False, error=str(e))

    async def delete_file(self, object_key: str) -> CloudDeleteResponse:
        """
        删除COS中的文件

        Args:
            object_key: 对象键

        Returns:
            删除响应信息
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=object_key)

            logger.info("文件删除成功: %s", object_key)
            return CloudDeleteResponse(success=True, object_key=object_key)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("文件删除失败: %s, 错误: %s", object_key, str(e))
            return CloudDeleteResponse(success=False, error=str(e))

    async def get_file_url(self, object_key: str, expires: int = 315360000) -> str:
        """
        获取文件的临时访问URL（预签名URL）

        Args:
            object_key: 对象键
            expires: 过期时间（秒），默认10年

        Returns:
            临时访问URL
        """
        try:
            url = self.client.get_presigned_url(
                Method="GET", Bucket=self.bucket, Key=object_key, Expired=expires
            )
            return url
        except Exception as e:
            logger.error("获取文件URL失败: %s, 错误: %s", object_key, str(e))
            raise

    async def get_resource_url(self, object_key: str) -> str:
        """
        获取文件的资源访问URL（公开访问链接）

        Args:
            object_key: 对象键

        Returns:
            资源访问URL
        """
        try:
            url = self.client.get_object_url(Bucket=self.bucket, Key=object_key)
            logger.info("生成资源访问URL成功: %s", object_key)
            return url
        except Exception as e:
            logger.error("获取资源访问URL失败: %s, 错误: %s", object_key, str(e))
            raise

    def _get_content_type(self, object_key: str) -> str:
        """
        根据文件扩展名获取内容类型

        Args:
            object_key: 对象键

        Returns:
            内容类型
        """
        ext = os.path.splitext(object_key)[1].lower()
        content_types = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".json": "application/json",
            ".xml": "application/xml",
            ".zip": "application/zip",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        return content_types.get(ext, "application/octet-stream")
