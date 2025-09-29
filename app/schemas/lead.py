"""
线索相关的 Pydantic Schema 定义

用于 API 请求和响应的数据验证和序列化
"""

from datetime import datetime
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, ConfigDict

class LeadBase(BaseModel):
    """线索基础 Schema"""
    category_id: Annotated[Optional[int], Field(None, description="线索类型ID：关联lead_categories表")]
    sub_category_id: Annotated[Optional[int], Field(None, description="子类型ID：关联lead_categories表的二级分类")]

    # 分配信息
    advisor_group_id: Annotated[Optional[int], Field(None, description="分配的顾问组ID")]
    advisor_group_sub_id: Annotated[Optional[int], Field(None, description="分配的顾问组子ID")]
    advisor_id: Annotated[Optional[int], Field(None, description="分配的顾问ID")]

    # 客户基础信息
    customer_id: Annotated[Optional[int], Field(None, description="客户ID")]
    customer_name: Annotated[Optional[str], Field(None, max_length=50, description="客户姓名")]
    customer_phone: Annotated[Optional[str], Field(None, max_length=20, description="客户电话：主要联系方式")]
    customer_email: Annotated[Optional[str], Field(None, max_length=100, description="客户邮箱")]
    customer_wechat_name: Annotated[Optional[str], Field(None, max_length=50, description="客户微信昵称")]
    customer_wechat_number: Annotated[Optional[str], Field(None, max_length=50, description="客户微信号码")]

    # 状态字段
    call_status_id: Annotated[Optional[int], Field(None, description="电话主状态ID：关联call_status表")]
    call_sub_status_id: Annotated[Optional[int], Field(None, description="电话子状态ID：关联call_status表的二级分类")]
    wechat_status_id: Annotated[Optional[int], Field(None, description="微信主状态ID：关联wechat_status表")]
    wechat_sub_status_id: Annotated[Optional[int], Field(None, description="微信子状态ID：关联wechat_status表的二级分类")]

    # 私域状态
    private_domain_review_status_id: Annotated[Optional[int], Field(None, description="私域回看主状态ID：关联private_domain_review_status表")]
    private_domain_review_sub_status_id: Annotated[Optional[int], Field(None, description="私域回看子状态ID：关联private_domain_review_status表的二级分类")]
    private_domain_participation_status_id: Annotated[Optional[int], Field(None, description="私域参加主状态ID：关联private_domain_participation_status表")]
    private_domain_participation_sub_status_id: Annotated[Optional[int], Field(None, description="私域参加子状态ID：关联private_domain_participation_status表的二级分类")]

    # 日程和合同状态
    schedule_status_id: Annotated[Optional[int], Field(None, description="日程主状态ID：关联schedule_status表")]
    schedule_sub_status_id: Annotated[Optional[int], Field(None, description="日程子状态ID：关联schedule_status表的二级分类")]
    schedule_times: Annotated[int, Field(0, description="日程次数")]
    contract_status_id: Annotated[Optional[int], Field(None, description="合同主状态ID：关联contract_status表")]
    contract_sub_status_id: Annotated[Optional[int], Field(None, description="合同子状态ID：关联contract_status表的二级分类")]

    # 分析字段
    analysis_failed_records: Annotated[int, Field(0, description="未能联系次数")]
    last_contact_record_id: Annotated[Optional[int], Field(None, description="最后一次可联系通话ID")]
    last_contact_time: Annotated[Optional[datetime], Field(None, description="最后一次可联系时间")]
    last_analysis_failed_record_id: Annotated[Optional[int], Field(None, description="最后一次未能联系通话ID")]
    last_analysis_failed_time: Annotated[Optional[datetime], Field(None, description="最后一次未能联系时间")]


class LeadCreate(LeadBase):
    """创建线索的 Schema"""

class LeadUpdate(LeadBase):
    """更新线索的 Schema"""

class LeadResponse(LeadBase):
    """线索响应 Schema"""
    id: Annotated[int, Field(..., description="主键ID")]
    created_at: Annotated[datetime, Field(..., description="创建时间")]
    updated_at: Annotated[datetime, Field(..., description="更新时间")]
    model_config = ConfigDict(from_attributes=True)

class LeadListResponse(BaseModel):
    """线索列表响应 Schema"""
    items: Annotated[List[LeadResponse], Field(..., description="线索列表")]
    total: Annotated[int, Field(..., description="总数量")]
    page: Annotated[int, Field(..., description="当前页码")]
    size: Annotated[int, Field(..., description="每页数量")]
    pages: Annotated[int, Field(..., description="总页数")]


class LeadQueryParams(BaseModel):
    """线索查询参数 Schema"""
    page: Annotated[int, Field(1, ge=1, description="页码，从1开始")]
    size: Annotated[int, Field(10, ge=1, le=100, description="每页数量，最大100")]

    # 基础分类信息
    category_id: Annotated[Optional[int], Field(None, description="线索类型ID")]
    sub_category_id: Annotated[Optional[int], Field(None, description="子类型ID")]

    # 分配信息
    advisor_group_id: Annotated[Optional[int], Field(None, description="顾问组ID")]
    advisor_group_sub_id: Annotated[Optional[int], Field(None, description="顾问组子ID")]
    advisor_id: Annotated[Optional[int], Field(None, description="顾问ID")]

    # 客户基础信息
    customer_id: Annotated[Optional[int], Field(None, description="客户ID")]
    customer_name: Annotated[Optional[str], Field(None, description="客户姓名")]
    customer_phone: Annotated[Optional[str], Field(None, description="客户电话")]
    customer_email: Annotated[Optional[str], Field(None, description="客户邮箱")]
    customer_wechat_name: Annotated[Optional[str], Field(None, description="客户微信昵称")]
    customer_wechat_number: Annotated[Optional[str], Field(None, description="客户微信号码")]

    # 电话状态（主状态+子状态）
    call_status_id: Annotated[Optional[int], Field(None, description="电话主状态ID")]
    call_sub_status_id: Annotated[Optional[int], Field(None, description="电话子状态ID")]

    # 微信状态（主状态+子状态）
    wechat_status_id: Annotated[Optional[int], Field(None, description="微信主状态ID")]
    wechat_sub_status_id: Annotated[Optional[int], Field(None, description="微信子状态ID")]

    # 私域回看状态（主状态+子状态）
    private_domain_review_status_id: Annotated[Optional[int], Field(None, description="私域回看主状态ID")]
    private_domain_review_sub_status_id: Annotated[Optional[int], Field(None, description="私域回看子状态ID")]

    # 私域参加状态（主状态+子状态）
    private_domain_participation_status_id: Annotated[Optional[int], Field(None, description="私域参加主状态ID")]
    private_domain_participation_sub_status_id: Annotated[Optional[int], Field(None, description="私域参加子状态ID")]

    # 日程状态（主状态+子状态）
    schedule_status_id: Annotated[Optional[int], Field(None, description="日程主状态ID")]
    schedule_sub_status_id: Annotated[Optional[int], Field(None, description="日程子状态ID")]
    schedule_times: Annotated[Optional[int], Field(None, description="日程次数")]

    # 合同状态（主状态+子状态）
    contract_status_id: Annotated[Optional[int], Field(None, description="合同主状态ID")]
    contract_sub_status_id: Annotated[Optional[int], Field(None, description="合同子状态ID")]

    # 分析字段
    analysis_failed_records: Annotated[Optional[int], Field(None, description="未能联系次数")]
    last_contact_record_id: Annotated[Optional[int], Field(None, description="最后一次可联系通话ID")]
    last_contact_time_start: Annotated[Optional[datetime], Field(None, description="最后一次可联系时间开始")]
    last_contact_time_end: Annotated[Optional[datetime], Field(None, description="最后一次可联系时间结束")]
    last_analysis_failed_record_id: Annotated[Optional[int], Field(None, description="最后一次未能联系通话ID")]
    last_analysis_failed_time_start: Annotated[Optional[datetime], Field(None, description="最后一次未能联系时间开始")]
    last_analysis_failed_time_end: Annotated[Optional[datetime], Field(None, description="最后一次未能联系时间结束")]

    # 时间范围查询
    created_at_start: Annotated[Optional[datetime], Field(None, description="创建时间开始")]
    created_at_end: Annotated[Optional[datetime], Field(None, description="创建时间结束")]
    updated_at_start: Annotated[Optional[datetime], Field(None, description="更新时间开始")]
    updated_at_end: Annotated[Optional[datetime], Field(None, description="更新时间结束")]

    # 搜索关键词
    search: Annotated[Optional[str], Field(None, description="搜索关键词（客户姓名、电话、线索编号、微信昵称、微信号码）")]

    # 排序字段
    sort_field: Annotated[str, Field("created_at", description="排序字段")]
    sort_order: Annotated[str, Field("desc", description="排序方向：asc或desc")]


class StatusItem(BaseModel):
    """状态项 Schema"""
    status_id: Annotated[int, Field(..., description="状态ID")]
    status_code: Annotated[str, Field(..., description="状态代码")]
    status_name: Annotated[str, Field(..., description="状态名称")]
    parent_id: Annotated[Optional[int], Field(None, description="父级状态ID")]
    sort_order: Annotated[Optional[int], Field(None, description="排序顺序")]
    is_active: Annotated[bool, Field(..., description="是否激活")]


class StatusMappingResponse(BaseModel):
    """状态映射响应 Schema"""
    status_type: Annotated[str, Field(..., description="状态类型")]
    type_name: Annotated[str, Field(..., description="类型名称")]
    status_list: Annotated[List[StatusItem], Field(..., description="状态列表")]
