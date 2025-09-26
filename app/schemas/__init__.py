"""
Pydantic schemas package
"""
# Pydantic schemas package
from .base import (
    ResponseData,
    SuccessResponse,
    ErrorResponse,
    PaginationInfo,
    PaginatedData,
    PaginatedResponse,
    ResponseCode,
    ResponseBuilder,
    BaseResponse,
)
from .advisor_call_duration_stats import (
    AdvisorCallDurationStatsBase,
    AdvisorCallDurationStatsResponse,
    AdvisorCallDurationStatsUpsertRequest,
)
from .file_record import FileUploadRequest, FileUploadResponse
from .lead import (
    LeadBase,
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadListResponse,
    LeadQueryParams,
)
from .scheduled_tasks import (
    ScheduledTaskBase,
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    ScheduledTaskResponse,
    TaskExecutionLogBase,
    TaskExecutionLogCreate,
    TaskExecutionLogResponse,
    TaskExecutionLogWithTask,
    ScheduledTaskListResponse,
    ScheduledTaskDetailResponse,
    TaskExecutionLogListResponse,
    TaskExecutionLogDetailResponse,
    TaskExecutionLogCreateResponse,
)

__all__ = [
    # Base schemas
    "ResponseData",
    "SuccessResponse",
    "ErrorResponse",
    "PaginationInfo",
    "PaginatedData",
    "PaginatedResponse",
    "ResponseCode",
    "ResponseBuilder",
    "BaseResponse",
    # Advisor call duration stats schemas
    "AdvisorCallDurationStatsBase",
    "AdvisorCallDurationStatsResponse",
    "AdvisorCallDurationStatsUpsertRequest",
    # File record schemas
    "FileUploadRequest",
    "FileUploadResponse",
    # Lead schemas
    "LeadBase",
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    "LeadListResponse",
    "LeadQueryParams",
    # Scheduled tasks schemas
    "ScheduledTaskBase",
    "ScheduledTaskCreate",
    "ScheduledTaskUpdate",
    "ScheduledTaskResponse",
    "TaskExecutionLogBase",
    "TaskExecutionLogCreate",
    "TaskExecutionLogResponse",
    "TaskExecutionLogWithTask",
    "ScheduledTaskListResponse",
    "ScheduledTaskDetailResponse",
    "TaskExecutionLogListResponse",
    "TaskExecutionLogDetailResponse",
    "TaskExecutionLogCreateResponse",
]
