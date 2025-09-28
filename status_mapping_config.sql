


-- =====================================================
-- 前端状态映射视图 - 简单数值映射
-- =====================================================

CREATE OR REPLACE VIEW v_frontend_status_mapping AS
SELECT 
    'call_status' as status_type,
    '电话状态' as type_name,
    id as value,
    code,
    name as label,
    parent_id,
    sort_order
FROM call_status 
WHERE status = 1

UNION ALL

SELECT 
    'wechat_status' as status_type,
    '微信状态' as type_name,
    id as value,
    code,
    name as label,
    parent_id,
    sort_order
FROM wechat_status 
WHERE status = 1

UNION ALL

SELECT 
    'private_domain_review_status' as status_type,
    '私域回看状态' as type_name,
    id as value,
    status_code as code,
    status_name as label,
    parent_id,
    sort_order
FROM private_domain_review_status 
WHERE is_active = TRUE

UNION ALL

SELECT 
    'private_domain_participation_status' as status_type,
    '私域参加状态' as type_name,
    id as value,
    status_code as code,
    status_name as label,
    parent_id,
    sort_order
FROM private_domain_participation_status 
WHERE is_active = TRUE

UNION ALL

SELECT 
    'schedule_status' as status_type,
    '日程状态' as type_name,
    id as value,
    code,
    name as label,
    parent_id,
    sort_order
FROM schedule_status 
WHERE status = 1

UNION ALL

SELECT 
    'contract_status' as status_type,
    '合同状态' as type_name,
    id as value,
    code,
    name as label,
    parent_id,
    sort_order
FROM contract_status 
WHERE status = 1

ORDER BY status_type, parent_id IS NOT NULL, sort_order;
