"""
线索相关的 Pydantic Schema 定义

用于 API 请求和响应的数据验证和序列化
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class LeadBase(BaseModel):
    """线索基础 Schema"""
    lead_no: str = Field(..., description="线索编号：业务唯一标识，格式如LEAD20240917001")
    category_id: int = Field(..., description="线索类型ID：关联lead_categories表")
    sub_category_id: Optional[int] = Field(None, description="子类型ID：关联lead_categories表的二级分类")
    
    # 分配信息
    advisor_group_id: Optional[int] = Field(None, description="分配的顾问组ID")
    advisor_group_sub_id: Optional[int] = Field(None, description="分配的顾问组子ID")
    advisor_id: Optional[int] = Field(None, description="分配的顾问ID")
    
    # 客户基础信息
    customer_id: Optional[int] = Field(None, description="客户ID")
    customer_name: Optional[str] = Field(None, max_length=50, description="客户姓名")
    customer_phone: Optional[str] = Field(None, max_length=20, description="客户电话：主要联系方式")
    customer_email: Optional[str] = Field(None, max_length=100, description="客户邮箱")
    customer_wechat_name: Optional[str] = Field(None, max_length=50, description="客户微信昵称")
    customer_wechat_number: Optional[str] = Field(None, max_length=50, description="客户微信号码")
    
    # 状态字段
    call_status_id: Optional[int] = Field(None, description="电话主状态ID：关联call_status表")
    call_sub_status_id: Optional[int] = Field(None, description="电话子状态ID：关联call_status表的二级分类")
    wechat_status_id: Optional[int] = Field(None, description="微信主状态ID：关联wechat_status表")
    wechat_sub_status_id: Optional[int] = Field(None, description="微信子状态ID：关联wechat_status表的二级分类")
    
    # 私域状态
    private_domain_review_status_id: Optional[int] = Field(None, description="私域回看主状态ID：关联private_domain_review_status表")
    private_domain_review_sub_status_id: Optional[int] = Field(None, description="私域回看子状态ID：关联private_domain_review_status表的二级分类")
    private_domain_participation_status_id: Optional[int] = Field(None, description="私域参加主状态ID：关联private_domain_participation_status表")
    private_domain_participation_sub_status_id: Optional[int] = Field(None, description="私域参加子状态ID：关联private_domain_participation_status表的二级分类")
    
    # 日程和合同状态
    schedule_status_id: Optional[int] = Field(None, description="日程主状态ID：关联schedule_status表")
    schedule_sub_status_id: Optional[int] = Field(None, description="日程子状态ID：关联schedule_status表的二级分类")
    schedule_times: int = Field(0, description="日程次数")
    contract_status_id: Optional[int] = Field(None, description="合同主状态ID：关联contract_status表")
    contract_sub_status_id: Optional[int] = Field(None, description="合同子状态ID：关联contract_status表的二级分类")
    
    # 分析字段
    analysis_failed_records: int = Field(0, description="未能联系次数")
    last_contact_record_id: Optional[int] = Field(None, description="最后一次可联系通话ID")
    last_contact_time: Optional[datetime] = Field(None, description="最后一次可联系时间")
    last_analysis_failed_record_id: Optional[int] = Field(None, description="最后一次未能联系通话ID")
    last_analysis_failed_time: Optional[datetime] = Field(None, description="最后一次未能联系时间")


class LeadCreate(LeadBase):
    """创建线索的 Schema"""
    pass


class LeadUpdate(BaseModel):
    """更新线索的 Schema"""
    lead_no: Optional[str] = Field(None, description="线索编号")
    category_id: Optional[int] = Field(None, description="线索类型ID")
    sub_category_id: Optional[int] = Field(None, description="子类型ID")
    
    # 分配信息
    advisor_group_id: Optional[int] = Field(None, description="分配的顾问组ID")
    advisor_group_sub_id: Optional[int] = Field(None, description="分配的顾问组子ID")
    advisor_id: Optional[int] = Field(None, description="分配的顾问ID")
    
    # 客户基础信息
    customer_id: Optional[int] = Field(None, description="客户ID")
    customer_name: Optional[str] = Field(None, max_length=50, description="客户姓名")
    customer_phone: Optional[str] = Field(None, max_length=20, description="客户电话")
    customer_email: Optional[str] = Field(None, max_length=100, description="客户邮箱")
    customer_wechat_name: Optional[str] = Field(None, max_length=50, description="客户微信昵称")
    customer_wechat_number: Optional[str] = Field(None, max_length=50, description="客户微信号码")
    
    # 状态字段
    call_status_id: Optional[int] = Field(None, description="电话主状态ID")
    call_sub_status_id: Optional[int] = Field(None, description="电话子状态ID")
    wechat_status_id: Optional[int] = Field(None, description="微信主状态ID")
    wechat_sub_status_id: Optional[int] = Field(None, description="微信子状态ID")
    
    # 私域状态
    private_domain_review_status_id: Optional[int] = Field(None, description="私域回看主状态ID")
    private_domain_review_sub_status_id: Optional[int] = Field(None, description="私域回看子状态ID")
    private_domain_participation_status_id: Optional[int] = Field(None, description="私域参加主状态ID")
    private_domain_participation_sub_status_id: Optional[int] = Field(None, description="私域参加子状态ID")
    
    # 日程和合同状态
    schedule_status_id: Optional[int] = Field(None, description="日程主状态ID")
    schedule_sub_status_id: Optional[int] = Field(None, description="日程子状态ID")
    schedule_times: Optional[int] = Field(None, description="日程次数")
    contract_status_id: Optional[int] = Field(None, description="合同主状态ID")
    contract_sub_status_id: Optional[int] = Field(None, description="合同子状态ID")
    
    # 分析字段
    analysis_failed_records: Optional[int] = Field(None, description="未能联系次数")
    last_contact_record_id: Optional[int] = Field(None, description="最后一次可联系通话ID")
    last_contact_time: Optional[datetime] = Field(None, description="最后一次可联系时间")
    last_analysis_failed_record_id: Optional[int] = Field(None, description="最后一次未能联系通话ID")
    last_analysis_failed_time: Optional[datetime] = Field(None, description="最后一次未能联系时间")


class LeadResponse(LeadBase):
    """线索响应 Schema"""
    id: int = Field(..., description="主键ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)


class LeadListResponse(BaseModel):
    """线索列表响应 Schema"""
    items: List[LeadResponse] = Field(..., description="线索列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class LeadQueryParams(BaseModel):
    """线索查询参数 Schema"""
    page: int = Field(1, ge=1, description="页码，从1开始")
    size: int = Field(10, ge=1, le=100, description="每页数量，最大100")
    category_id: Optional[int] = Field(None, description="线索类型ID")
    advisor_id: Optional[int] = Field(None, description="顾问ID")
    customer_phone: Optional[str] = Field(None, description="客户电话")
    call_status_id: Optional[int] = Field(None, description="电话状态ID")
    wechat_status_id: Optional[int] = Field(None, description="微信状态ID")
    created_at_start: Optional[datetime] = Field(None, description="创建时间开始")
    created_at_end: Optional[datetime] = Field(None, description="创建时间结束")
    search: Optional[str] = Field(None, description="搜索关键词（客户姓名、电话、线索编号）")
