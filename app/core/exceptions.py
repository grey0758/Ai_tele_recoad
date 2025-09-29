"""
异常定义模块
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AITeleException(HTTPException):
    """AI Tele异常"""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class DatabaseException(AITeleException):
    """数据库异常"""
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class ValidationException(AITeleException):
    """验证异常"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class NotFoundException(AITeleException):
    """资源不存在异常"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(AITeleException):
    """未授权异常"""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(AITeleException):
    """禁止访问异常"""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ExternalRequestException(AITeleException):
    """外部请求异常"""
    def __init__(self, detail: str = "External request failed"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
