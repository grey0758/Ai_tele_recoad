
-- =====================================================
-- 状态配置视图 - 统一前端状态映射
-- 用途：为前端提供统一的状态配置数据
-- 命名规范：使用下划线分隔，语义清晰
-- =====================================================

-- 删除旧视图
DROP VIEW IF EXISTS view_lead_status_mapping;

-- 创建新的状态配置视图
CREATE VIEW view_lead_status_mapping AS
SELECT 
    'call_status' AS status_type,
    '电话状态' AS type_name,
    id AS status_id,
    code AS status_code,
    name AS status_name,
    parent_id,
    sort_order,
    is_active,
    created_at,
    updated_at
FROM call_status 
WHERE is_active = TRUE

UNION ALL

SELECT 
    'wechat_status' AS status_type,
    '微信状态' AS type_name,
    id AS status_id,
    code AS status_code,
    name AS status_name,
    parent_id,
    sort_order,
    is_active,
    created_at,
    updated_at
FROM wechat_status 
WHERE is_active = TRUE

UNION ALL

SELECT 
    'private_domain_review_status' AS status_type,
    '私域回看状态' AS type_name,
    id AS status_id,
    code AS status_code,
    name AS status_name,
    parent_id,
    sort_order,
    is_active,
    created_at,
    updated_at
FROM private_domain_review_status 
WHERE is_active = TRUE

UNION ALL

SELECT 
    'private_domain_participation_status' AS status_type,
    '私域参加状态' AS type_name,
    id AS status_id,
    code AS status_code,
    name AS status_name,
    parent_id,
    sort_order,
    is_active,
    created_at,
    updated_at
FROM private_domain_participation_status 
WHERE is_active = TRUE

UNION ALL

SELECT 
    'schedule_status' AS status_type,
    '日程状态' AS type_name,
    id AS status_id,
    code AS status_code,
    name AS status_name,
    parent_id,
    sort_order,
    is_active,
    created_at,
    updated_at
FROM schedule_status 
WHERE is_active = TRUE

UNION ALL

SELECT 
    'contract_status' AS status_type,
    '合同状态' AS type_name,
    id AS status_id,
    code AS status_code,
    name AS status_name,
    parent_id,
    sort_order,
    is_active,
    created_at,
    updated_at
FROM contract_status 
WHERE is_active = TRUE
