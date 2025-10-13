-- =====================================================
-- 删除所有表的SQL语句
-- 注意：由于存在外键约束，需要按照依赖关系的逆序删除
-- =====================================================
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `lead_status_logs`;
DROP TABLE IF EXISTS `call_records`;
DROP TABLE IF EXISTS `leads`;
DROP TABLE IF EXISTS `advisors`;
DROP TABLE IF EXISTS `advisor_groups`;
DROP TABLE IF EXISTS `contract_status`;
DROP TABLE IF EXISTS `schedule_status`;
DROP TABLE IF EXISTS `private_domain_participation_status`;
DROP TABLE IF EXISTS `private_domain_review_status`;
DROP TABLE IF EXISTS `wechat_status`;
DROP TABLE IF EXISTS `call_status`;
DROP TABLE IF EXISTS `lead_categories`;

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- 第一步：创建基础配置表（无外键依赖）
-- =====================================================

-- 线索类型配置表
CREATE TABLE lead_categories (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '类型名称：如直播、公海、旧线索等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '类型编码：用于程序识别，如LIVE、PUBLIC、OLD',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用：控制状态可用性',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_active (parent_id, is_active),
    INDEX idx_code (code),

    -- 外键约束：自引用
    FOREIGN KEY (parent_id) REFERENCES lead_categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='线索类型配置表';

-- 电话状态表
CREATE TABLE call_status (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '状态名称：如未联系、空号、未接听、已接听等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '状态编码：用于程序识别，如UNCONTACTED、EMPTY、UNANSWERED、ANSWERED',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用：控制状态可用性',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_active (parent_id, is_active),
    INDEX idx_code (code),

    -- 外键约束：自引用
    FOREIGN KEY (parent_id) REFERENCES call_status(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电话状态表';

-- 微信状态表
CREATE TABLE wechat_status (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '状态名称：如未添加、已添加等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '状态编码：用于程序识别，如NOT_ADDED、ADDED',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    config JSON COMMENT '状态配置信息：包含描述、后续动作、统计权重等',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用：控制状态可用性',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_active (parent_id, is_active),
    INDEX idx_code (code),

    -- 外键约束：自引用
    FOREIGN KEY (parent_id) REFERENCES wechat_status(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='微信状态表';

-- 私域回看状态表
CREATE TABLE private_domain_review_status (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '状态名称：如发私域、未看回看、已看回看等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '状态编码：用于程序识别，如SENT_TO_PRIVATE、NOT_VIEWED_REVIEW、VIEWED_REVIEW',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用：控制状态可用性',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_active (parent_id, is_active),
    INDEX idx_code (code),

    -- 外键约束：自引用
    FOREIGN KEY (parent_id) REFERENCES private_domain_review_status(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='私域回看状态表';

-- 私域参加状态表
CREATE TABLE private_domain_participation_status (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '状态名称：如参加私域、未参加、已经参加等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '状态编码：用于程序识别，如PARTICIPATION、NOT_PARTICIPATED、PARTICIPATED',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用：控制状态可用性',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_active (parent_id, is_active),
    INDEX idx_code (code),

    -- 外键约束：自引用
    FOREIGN KEY (parent_id) REFERENCES private_domain_participation_status(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='私域参加状态表';

-- 日程状态表
CREATE TABLE schedule_status (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '状态名称：如未约日程、已约日程等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '状态编码：用于程序识别',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    config JSON COMMENT '状态配置信息：包含描述、后续动作、统计权重等',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用：控制状态可用性',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_active (parent_id, is_active),
    INDEX idx_code (code),

    -- 外键约束：自引用
    FOREIGN KEY (parent_id) REFERENCES schedule_status(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日程状态表';

-- 合同状态表
CREATE TABLE contract_status (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '状态名称：如未拉群、已经拉群、已签合同、已收款等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '状态编码：用于程序识别',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    config JSON COMMENT '状态配置信息：包含描述、后续动作、统计权重等',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用：控制状态可用性',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_active (parent_id, is_active),
    INDEX idx_code (code),

    -- 外键约束：自引用
    FOREIGN KEY (parent_id) REFERENCES contract_status(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='合同状态表';

-- =====================================================
-- 第二步：创建顾问相关表
-- =====================================================

-- 顾问组表
CREATE TABLE advisor_groups (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(30) NOT NULL COMMENT '组名：如一号组、二号组等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '组编码：用于程序识别',
    leader_id SMALLINT COMMENT '组长ID：关联advisors表，但不设外键避免循环依赖',
    lead_category_id TINYINT COMMENT '线索类型ID：关联lead_categories表，指定该组负责的线索类型',
    parent_id TINYINT COMMENT '父组ID：支持组层级结构，顶级组为NULL',
    settings JSON COMMENT '组设置：工作时间、分配规则、最大线索数等配置信息',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用：控制状态可用性',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计
    INDEX idx_code (code),
    INDEX idx_active (is_active),
    INDEX idx_lead_category (lead_category_id),
    INDEX idx_parent_id (parent_id),

    -- 外键约束
    FOREIGN KEY (lead_category_id) REFERENCES lead_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_id) REFERENCES advisor_groups(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='顾问组表';

-- 顾问表
CREATE TABLE advisors (
    id SMALLINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    group_id TINYINT NOT NULL COMMENT '所属组ID',
    sub_group_id TINYINT COMMENT '所属子组ID：支持顾问分配到子组',
    name VARCHAR(50) NOT NULL COMMENT '顾问姓名',
    status TINYINT DEFAULT 1 COMMENT '状态：1=在职，0=离职，2=休假',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计
    INDEX idx_group_status (group_id, status),
    INDEX idx_sub_group_status (sub_group_id, status),
    INDEX idx_status (status),

    -- 外键约束
    FOREIGN KEY (group_id) REFERENCES advisor_groups(id) ON DELETE RESTRICT,
    FOREIGN KEY (sub_group_id) REFERENCES advisor_groups(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='顾问表';

-- =====================================================
-- 第三步：创建线索主表
-- =====================================================

-- 线索主表
CREATE TABLE leads (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID，使用BIGINT支持大数据量',

    -- 核心分类信息
    category_id TINYINT COMMENT '线索类型ID：关联lead_categories表',
    sub_category_id TINYINT COMMENT '子类型ID：关联lead_categories表的二级分类',

    -- 分配信息
    advisor_group_id TINYINT COMMENT '分配的顾问组ID',
    advisor_group_sub_id TINYINT COMMENT '分配的顾问组子ID',
    advisor_id SMALLINT COMMENT '分配的顾问ID',

    -- 客户基础信息
    customer_id BIGINT COMMENT '客户ID',
    customer_name VARCHAR(50) COMMENT '客户姓名',
    customer_phone VARCHAR(20) COMMENT '客户电话：主要联系方式',
    customer_email VARCHAR(100) COMMENT '客户邮箱',
    customer_wechat_name VARCHAR(50) COMMENT '客户微信昵称',
    customer_wechat_number VARCHAR(50) COMMENT '客户微信号码',

    -- 状态字段（主状态+子状态设计）
    call_status_id TINYINT COMMENT '电话主状态ID',
    call_sub_status_id TINYINT COMMENT '电话子状态ID',
    
    wechat_status_id TINYINT COMMENT '微信主状态ID',   
    wechat_sub_status_id TINYINT COMMENT '微信子状态ID',
    
    -- 两个独立的私域状态
    private_domain_review_status_id TINYINT COMMENT '私域回看主状态ID',
    private_domain_review_sub_status_id TINYINT COMMENT '私域回看子状态ID',
    
    private_domain_participation_status_id TINYINT COMMENT '私域参加主状态ID',
    private_domain_participation_sub_status_id TINYINT COMMENT '私域参加子状态ID',
    
    schedule_status_id TINYINT COMMENT '日程主状态ID',
    schedule_sub_status_id TINYINT COMMENT '日程子状态ID',
    schedule_times TINYINT DEFAULT 0 COMMENT '日程次数',
    
    contract_status_id TINYINT COMMENT '合同主状态ID',
    contract_sub_status_id TINYINT COMMENT '合同子状态ID',

    -- 分析字段
    analysis_failed_records TINYINT DEFAULT 0 COMMENT '未能联系次数',
    last_contact_record_id BIGINT COMMENT '最后一次可联系通话ID',
    last_contact_time TIMESTAMP COMMENT '最后一次可联系时间',
    last_analysis_failed_record_id BIGINT COMMENT '最后一次未能联系通话ID',
    last_analysis_failed_time TIMESTAMP COMMENT '最后一次未能联系时间',

    -- 时间字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 性能优化索引
    INDEX idx_category_advisor (category_id, advisor_id),
    INDEX idx_advisor_status (advisor_id, call_status_id),
    INDEX idx_phone (customer_phone),
    INDEX idx_created_category (created_at, category_id),
    INDEX idx_status_combination (call_status_id, wechat_status_id, schedule_status_id),

    -- 外键约束
    FOREIGN KEY (category_id) REFERENCES lead_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (sub_category_id) REFERENCES lead_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (advisor_group_id) REFERENCES advisor_groups(id) ON DELETE SET NULL,
    FOREIGN KEY (advisor_id) REFERENCES advisors(id) ON DELETE SET NULL,
    
    -- 状态表外键约束
    FOREIGN KEY (call_status_id) REFERENCES call_status(id) ON DELETE SET NULL,
    FOREIGN KEY (call_sub_status_id) REFERENCES call_status(id) ON DELETE SET NULL,
    
    FOREIGN KEY (wechat_status_id) REFERENCES wechat_status(id) ON DELETE SET NULL,
    FOREIGN KEY (wechat_sub_status_id) REFERENCES wechat_status(id) ON DELETE SET NULL,
    
    -- 两个独立私域状态的外键约束
    FOREIGN KEY (private_domain_review_status_id) REFERENCES private_domain_review_status(id) ON DELETE SET NULL,
    FOREIGN KEY (private_domain_review_sub_status_id) REFERENCES private_domain_review_status(id) ON DELETE SET NULL,
    
    FOREIGN KEY (private_domain_participation_status_id) REFERENCES private_domain_participation_status(id) ON DELETE SET NULL,
    FOREIGN KEY (private_domain_participation_sub_status_id) REFERENCES private_domain_participation_status(id) ON DELETE SET NULL,
    
    FOREIGN KEY (schedule_status_id) REFERENCES schedule_status(id) ON DELETE SET NULL,
    FOREIGN KEY (schedule_sub_status_id) REFERENCES schedule_status(id) ON DELETE SET NULL,
    
    FOREIGN KEY (contract_status_id) REFERENCES contract_status(id) ON DELETE SET NULL,
    FOREIGN KEY (contract_sub_status_id) REFERENCES contract_status(id) ON DELETE SET NULL

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='线索主表-系统核心业务表（独立私域状态设计）';

-- =====================================================
-- 第四步：创建依赖线索表的其他表
-- =====================================================

-- 通话记录表
CREATE TABLE call_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID，使用BIGINT支持大数据量',
    
    -- CallRecordUploadRequest 主要字段
    dev_id VARCHAR(200) NOT NULL COMMENT '设备ID',
    record_id INT NOT NULL COMMENT '记录ID',
    ch TINYINT NOT NULL COMMENT '通道号',
    begin_time BIGINT NOT NULL COMMENT '开始时间戳',
    end_time BIGINT NOT NULL COMMENT '结束时间戳',
    time_len INT NOT NULL COMMENT '通话时长(秒)',
    call_type ENUM('callIn', 'callOut', 'callInNoAnswer', 'callOutNoAnswer') NOT NULL COMMENT '通话类型',
    phone VARCHAR(20) NOT NULL COMMENT '电话号码',
    dtmf_keys VARCHAR(100) DEFAULT '' COMMENT 'DTMF按键',
    ring_count INT DEFAULT 0 COMMENT '振铃次数',
    file_size BIGINT NOT NULL COMMENT '文件大小(字节)',
    file_name VARCHAR(255) NOT NULL COMMENT '文件路径',
    custom_id VARCHAR(100) DEFAULT '' COMMENT '自定义ID',
    record_uuid VARCHAR(36) UNIQUE COMMENT '记录UUID',
    upload_state TINYINT NOT NULL COMMENT '上传状态',
    
    -- 存储信息
    local_path VARCHAR(500) COMMENT '本地文件路径',
    cloud_url VARCHAR(500) COMMENT '云存储URL',
    cloud_uploaded BOOLEAN DEFAULT FALSE COMMENT '是否已上传到云存储',
    
    -- 业务扩展字段
    call_no VARCHAR(30) UNIQUE COMMENT '通话编号：业务唯一标识，格式如CALL20240917001',
    lead_id BIGINT COMMENT '关联的线索ID',
    advisor_id SMALLINT COMMENT '通话顾问ID',
    advisor_group_id TINYINT COMMENT '所属顾问组ID',
    advisor_group_sub_id TINYINT COMMENT '所属顾问组子ID',
    conversation_content TEXT COMMENT '对话记录：包含对话内容、关键信息提取、客户需求等',
    call_summary LONGTEXT COMMENT '通话总结：顾问填写的通话要点和后续跟进计划',
    call_quality_score TINYINT COMMENT '通话质量评分：1-100分，用于质检评估',
    quality_notes TEXT COMMENT '质检备注：质检人员的评价和建议',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引设计
    INDEX idx_dev_id (dev_id),
    INDEX idx_record_id (record_id),
    INDEX idx_phone (phone),
    INDEX idx_call_type (call_type),
    INDEX idx_begin_time (begin_time),
    INDEX idx_upload_state (upload_state),
    INDEX idx_cloud_uploaded (cloud_uploaded),
    INDEX idx_lead_id (lead_id),
    INDEX idx_advisor_id (advisor_id),
    INDEX idx_advisor_group (advisor_group_id),
    INDEX idx_call_type_time (call_type, begin_time),
    INDEX idx_phone_time (phone, begin_time),
    UNIQUE KEY uk_record_uuid (record_uuid),
    UNIQUE KEY uk_dev_record (dev_id, record_id),
    
    -- 外键约束
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
    FOREIGN KEY (advisor_id) REFERENCES advisors(id) ON DELETE RESTRICT,
    FOREIGN KEY (advisor_group_id) REFERENCES advisor_groups(id) ON DELETE SET NULL
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通话记录表';

-- 线索状态变更日志表
CREATE TABLE lead_status_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    
    -- 关联信息
    lead_id BIGINT NOT NULL COMMENT '线索ID',
    advisor_id SMALLINT COMMENT '操作顾问ID',
    
    -- 状态变更信息
    status_field VARCHAR(50) NOT NULL COMMENT '状态字段名',
    old_value TINYINT COMMENT '变更前的值',
    new_value TINYINT COMMENT '变更后的值',
    sub_status_field VARCHAR(50) COMMENT '子状态字段名',
    sub_old_value TINYINT COMMENT '变更前的子状态值',
    sub_new_value TINYINT COMMENT '变更后的子状态值',
    operation_description TEXT COMMENT '操作描述',
    notes TEXT COMMENT '备注',
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '变更时间',
    
    -- 索引
    INDEX idx_lead_time (lead_id, created_at),
    INDEX idx_advisor_time (advisor_id, created_at),
    INDEX idx_status_field (status_field),
    INDEX idx_sub_status_field (sub_status_field),
    
    -- 外键约束
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
    FOREIGN KEY (advisor_id) REFERENCES advisors(id) ON DELETE SET NULL
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='线索状态变更日志表';

-- =====================================================
-- 第五步：插入初始化数据
-- =====================================================

-- 线索类型表初始化数据
INSERT INTO lead_categories (name, code, parent_id, sort_order) VALUES
('直播间', 'LIVE', NULL, 1),
('视频号', 'VIDEO_ACCOUNT', NULL, 2),
('大麦公海', 'DAMAI_PUBLIC', NULL, 3),
('其他', 'OTHER', NULL, 4);

-- 获取直播的ID，用于创建子分类
SET @live_id = (SELECT id FROM lead_categories WHERE code = 'LIVE');

-- 直播的子分类
INSERT INTO lead_categories (name, code, parent_id, sort_order) VALUES
('直播间1-广州大麦-余焕文', 'LIVE_ROOM_1', @live_id, 1),
('直播间2-广州大麦-余焕文-AI智能体商业化', 'LIVE_ROOM_2', @live_id, 2),
('直播间3-广州大麦-余焕文-C', 'LIVE_ROOM_3', @live_id, 3),
('直播间4-广州大麦-资源对接-B', 'LIVE_ROOM_4', @live_id, 4),
('直播间5-广州大麦CEO-余焕文', 'LIVE_ROOM_5', @live_id, 5);

-- 电话状态初始化数据
INSERT INTO call_status (name, code, parent_id, sort_order) VALUES
('未联系', 'UNCONTACTED', NULL, 1),
('空号', 'EMPTY_NUMBER', NULL, 2),
('未接听', 'UNANSWERED', NULL, 3),
('已接听', 'ANSWERED', NULL, 4);

-- 获取已接听的ID
SET @answered_id = (SELECT id FROM call_status WHERE code = 'ANSWERED');

-- 已接听子状态
INSERT INTO call_status (name, code, parent_id, sort_order) VALUES
('没有需求', 'ANSWERED_NO_DEMAND', @answered_id, 1),
('有需求', 'ANSWERED_HAS_DEMAND', @answered_id, 2);

-- 微信状态初始化数据
INSERT INTO wechat_status (name, code, parent_id, sort_order) VALUES
('未添加', 'NOT_ADDED', NULL, 1),
('已添加', 'ADDED', NULL, 2);

-- 私域回看状态初始化数据
INSERT INTO private_domain_review_status (name, code, parent_id, sort_order) VALUES
('发私域', 'SENT_TO_PRIVATE', NULL, 1);

-- 获取发私域的ID，用于创建子分类
SET @sent_private_id = (SELECT id FROM private_domain_review_status WHERE code = 'SENT_TO_PRIVATE');

-- 发私域的子状态
INSERT INTO private_domain_review_status (name, code, parent_id, sort_order) VALUES
('未看回看', 'NOT_VIEWED_REVIEW', @sent_private_id, 1),
('已看回看', 'VIEWED_REVIEW', @sent_private_id, 2);

-- 私域参加状态初始化数据
INSERT INTO private_domain_participation_status (name, code, parent_id, sort_order) VALUES
('参加私域', 'PARTICIPATION', NULL, 1);

-- 获取参加私域的ID，用于创建子分类
SET @participation_id = (SELECT id FROM private_domain_participation_status WHERE code = 'PARTICIPATION');

-- 参加私域的子状态
INSERT INTO private_domain_participation_status (name, code, parent_id, sort_order) VALUES
('未参加', 'NOT_PARTICIPATED', @participation_id, 1),
('已经参加', 'PARTICIPATED', @participation_id, 2);

-- 日程状态初始化数据
INSERT INTO schedule_status (name, code, parent_id, sort_order) VALUES
('未约日程', 'NOT_SCHEDULED', NULL, 1),
('已约日程', 'SCHEDULED', NULL, 2);

-- 合同状态初始化数据
INSERT INTO contract_status (name, code, parent_id, sort_order) VALUES
('未拉群', 'NOT_GROUPED', NULL, 1),
('已经拉群', 'GROUPED', NULL, 2),
('已签合同', 'CONTRACT_SIGNED', NULL, 3),
('已收款', 'PAYMENT_RECEIVED', NULL, 4);

-- 顾问组初始化数据
INSERT INTO advisor_groups (name, code) VALUES
('一号组', 'GROUP_1'),
('二号组', 'GROUP_2'),
('三号组', 'GROUP_3');

-- 顾问初始化数据
INSERT INTO advisors (id, group_id, name, status, created_at, updated_at) VALUES
(1, 1, 'grey', 1, '2025-09-25 18:00:24', '2025-10-08 18:38:21'),
(2, 1, 'NIKO', 1, '2025-09-25 18:00:24', '2025-10-08 18:38:23'),
(3, 1, '俊涛', 1, '2025-09-26 11:00:36', '2025-10-08 18:38:24'),
(4, 1, '智浩', 1, '2025-09-26 11:10:56', '2025-10-08 18:38:25'),
(5, 1, '思怡', 1, '2025-09-26 11:11:19', '2025-10-08 18:38:26'),
(6, 1, '佳慧', 1, '2025-09-26 11:12:00', '2025-10-08 18:38:28'),

-- =====================================================
-- 第六步：插入测试数据
-- =====================================================

-- 插入60条测试数据到leads表
INSERT INTO leads (
    category_id, sub_category_id, advisor_group_id, advisor_id, 
    customer_name, customer_phone, customer_email, customer_wechat_name, customer_wechat_number,
    call_status_id, call_sub_status_id, wechat_status_id, wechat_sub_status_id,
    private_domain_review_status_id, private_domain_review_sub_status_id,
    private_domain_participation_status_id, private_domain_participation_sub_status_id,
    schedule_status_id, schedule_sub_status_id, contract_status_id, created_at
) VALUES
-- 第1-20条：直播线索 (category_id=1, sub_category_id=2,3,4,5,6)
(1, 2, 1, 1, '陈小明', '13800138001', 'chenxm@email.com', '阳光小陈', 'wx_chenxm01', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 2, '2024-09-17 08:30:00'),
(1, 3, 1, 2, '刘美丽', '13800138002', 'liuml@email.com', '美丽人生', 'wx_liuml02', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 1, '2024-09-17 09:15:00'),
(1, 4, 2, 3, '王大力', '13800138003', 'wangdl@email.com', '大力水手', 'wx_wangdl03', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-17 10:20:00'),
(1, 5, 1, 1, '李小花', '13800138004', 'lixh@email.com', '花花世界', 'wx_lixh04', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 3, '2024-09-17 11:45:00'),
(1, 6, 2, 4, '张强', '13800138005', 'zhangq@email.com', '强哥在线', 'wx_zhangq05', 2, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-17 13:10:00'),
(1, 2, 3, 5, '赵敏', '13800138006', 'zhaomin@email.com', '敏敏特穆尔', 'wx_zhaomin06', 4, 5, 2, NULL, 1, 3, 1, 3, 2, NULL, 4, '2024-09-17 14:30:00'),
(1, 3, 1, 2, '孙悟空', '13800138007', 'sunwk@email.com', '齐天大圣', 'wx_sunwk07', 1, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-17 15:45:00'),
(1, 4, 2, 3, '周杰伦', '13800138008', 'zhoujl@email.com', '周董', 'wx_zhoujl08', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 2, '2024-09-17 16:20:00'),
(1, 5, 3, 6, '林志玲', '13800138009', 'linzl@email.com', '志玲姐姐', 'wx_linzl09', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-17 17:15:00'),
(1, 6, 1, 1, '马云', '13800138010', 'mayun@email.com', '风清扬', 'wx_mayun10', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 1, '2024-09-17 18:30:00'),
(1, 2, 2, 4, '马化腾', '13800138011', 'maht@email.com', '小马哥', 'wx_maht11', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 3, '2024-09-17 19:15:00'),
(1, 3, 3, 5, '李彦宏', '13800138012', 'liyh@email.com', 'Robin', 'wx_liyh12', 2, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-17 20:30:00'),
(1, 4, 1, 2, '刘强东', '13800138013', 'liuqd@email.com', '东哥', 'wx_liuqd13', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 2, '2024-09-17 21:45:00'),
(1, 5, 2, 3, '雷军', '13800138014', 'leijun@email.com', '雷布斯', 'wx_leijun14', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-18 08:20:00'),
(1, 6, 3, 6, '任正非', '13800138015', 'renzf@email.com', '任总', 'wx_renzf15', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 4, '2024-09-18 09:35:00'),
(1, 2, 1, 1, '董明珠', '13800138016', 'dongmz@email.com', '董小姐', 'wx_dongmz16', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 1, '2024-09-18 10:50:00'),
(1, 3, 2, 4, '王健林', '13800138017', 'wangjl@email.com', '首富', 'wx_wangjl17', 1, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-18 12:15:00'),
(1, 4, 3, 5, '马斯克', '13800138018', 'musk@email.com', 'Elon', 'wx_musk18', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 3, '2024-09-18 13:30:00'),
(1, 5, 1, 2, '比尔盖茨', '13800138019', 'gates@email.com', 'Bill', 'wx_gates19', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-18 14:45:00'),
(1, 6, 2, 3, '乔布斯', '13800138020', 'jobs@email.com', 'Steve', 'wx_jobs20', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 2, '2024-09-18 16:00:00'),

-- 第21-40条：视频号线索 (category_id=2)
(2, NULL, 1, 1, '刘德华', '13800138021', 'liudh@email.com', '华仔', 'wx_liudh21', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 3, '2024-09-18 08:45:00'),
(2, NULL, 2, 4, '张学友', '13800138022', 'zhangxy@email.com', '歌神', 'wx_zhangxy22', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-18 09:30:00'),
(2, NULL, 3, 5, '郭富城', '13800138023', 'guofc@email.com', '城城', 'wx_guofc23', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 2, '2024-09-18 10:15:00'),
(2, NULL, 1, 2, '黎明', '13800138024', 'liming@email.com', '黎天王', 'wx_liming24', 2, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-18 11:20:00'),
(2, NULL, 2, 3, '梁朝伟', '13800138025', 'liangcw@email.com', '伟仔', 'wx_liangcw25', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 4, '2024-09-18 12:45:00'),
(2, NULL, 3, 6, '周星驰', '13800138026', 'zhouxc@email.com', '星爷', 'wx_zhouxc26', 1, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-18 13:30:00'),
(2, NULL, 1, 1, '成龙', '13800138027', 'chenglong@email.com', '大哥', 'wx_chenglong27', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 1, '2024-09-18 14:15:00'),
(2, NULL, 2, 4, '李连杰', '13800138028', 'lilj@email.com', '李师傅', 'wx_lilj28', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-18 15:45:00'),
(2, NULL, 3, 5, '甄子丹', '13800138029', 'zhenzd@email.com', '丹爷', 'wx_zhenzd29', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 3, '2024-09-18 16:30:00'),
(2, NULL, 1, 2, '吴京', '13800138030', 'wujing@email.com', '京哥', 'wx_wujing30', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 2, '2024-09-18 17:20:00'),
(2, NULL, 2, 3, '洪金宝', '13800138031', 'hongjb@email.com', '洪爷', 'wx_hongjb31', 2, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-18 18:15:00'),
(2, NULL, 3, 6, '元彪', '13800138032', 'yuanbiao@email.com', '彪哥', 'wx_yuanbiao32', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 4, '2024-09-18 19:30:00'),
(2, NULL, 1, 1, '元华', '13800138033', 'yuanhua@email.com', '华叔', 'wx_yuanhua33', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-18 20:45:00'),
(2, NULL, 2, 4, '袁和平', '13800138034', 'yuanhp@email.com', '八爷', 'wx_yuanhp34', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 1, '2024-09-19 08:20:00'),
(2, NULL, 3, 5, '徐克', '13800138035', 'xuke@email.com', '徐老怪', 'wx_xuke35', 1, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-19 09:35:00'),
(2, NULL, 1, 2, '王晶', '13800138036', 'wangjing@email.com', '王导', 'wx_wangjing36', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 3, '2024-09-19 10:50:00'),
(2, NULL, 2, 3, '杜琪峰', '13800138037', 'duqf@email.com', '杜sir', 'wx_duqf37', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 2, '2024-09-19 12:15:00'),
(2, NULL, 3, 6, '陈可辛', '13800138038', 'chenkx@email.com', '陈导', 'wx_chenkx38', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-19 13:30:00'),
(2, NULL, 1, 1, '尔冬升', '13800138039', 'erdsh@email.com', '升哥', 'wx_erdsh39', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 4, '2024-09-19 14:45:00'),
(2, NULL, 2, 4, '林超贤', '13800138040', 'lincx@email.com', '林导', 'wx_lincx40', 2, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-19 16:00:00'),

-- 第41-60条：大麦公海线索 (category_id=3)
(3, NULL, 1, 1, '范冰冰', '13800138041', 'fanbb@email.com', '冰冰', 'wx_fanbb41', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 1, '2024-09-19 08:20:00'),
(3, NULL, 2, 4, '章子怡', '13800138042', 'zhangzy@email.com', '子怡', 'wx_zhangzy42', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 3, '2024-09-19 09:45:00'),
(3, NULL, 3, 5, '赵薇', '13800138043', 'zhaowei@email.com', '小燕子', 'wx_zhaowei43', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-19 10:30:00'),
(3, NULL, 1, 2, '周迅', '13800138044', 'zhouxun@email.com', '迅哥', 'wx_zhouxun44', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 2, '2024-09-19 11:15:00'),
(3, NULL, 2, 3, '徐静蕾', '13800138045', 'xujl@email.com', '老徐', 'wx_xujl45', 1, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-19 12:40:00'),
(3, NULL, 3, 6, '舒淇', '13800138046', 'shuqi@email.com', '淇淇', 'wx_shuqi46', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 4, '2024-09-19 13:25:00'),
(3, NULL, 1, 1, '林心如', '13800138047', 'linxr@email.com', '紫薇', 'wx_linxr47', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 1, '2024-09-19 14:50:00'),
(3, NULL, 2, 4, '杨幂', '13800138048', 'yangmi@email.com', '大幂幂', 'wx_yangmi48', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-19 15:35:00'),
(3, NULL, 3, 5, '刘诗诗', '13800138049', 'liuss@email.com', '诗诗', 'wx_liuss49', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 3, '2024-09-19 16:20:00'),
(3, NULL, 1, 2, '唐嫣', '13800138050', 'tangyan@email.com', '糖糖', 'wx_tangyan50', 2, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-19 17:10:00'),
(3, NULL, 2, 3, '高圆圆', '13800138051', 'gaoyy@email.com', '圆圆', 'wx_gaoyy51', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 2, '2024-09-19 18:45:00'),
(3, NULL, 3, 6, '孙俪', '13800138052', 'sunli@email.com', '娘娘', 'wx_sunli52', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 4, '2024-09-20 08:30:00'),
(3, NULL, 1, 1, '白百何', '13800138053', 'baibh@email.com', '小白', 'wx_baibh53', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-20 09:15:00'),
(3, NULL, 2, 4, '马伊琍', '13800138054', 'maiyi@email.com', '伊琍', 'wx_maiyi54', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 1, '2024-09-20 10:45:00'),
(3, NULL, 3, 5, '姚晨', '13800138055', 'yaochen@email.com', '姚姚', 'wx_yaochen55', 1, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-20 11:30:00'),
(3, NULL, 1, 2, '海清', '13800138056', 'haiqing@email.com', '清清', 'wx_haiqing56', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 3, '2024-09-20 12:20:00'),
(3, NULL, 2, 3, '袁泉', '13800138057', 'yuanquan@email.com', '泉泉', 'wx_yuanquan57', 4, 5, 2, NULL, 1, 3, 1, 3, 1, NULL, 2, '2024-09-20 13:45:00'),
(3, NULL, 3, 6, '秦海璐', '13800138058', 'qinhl@email.com', '海璐', 'wx_qinhl58', 3, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-20 14:30:00'),
(3, NULL, 1, 1, '陶虹', '13800138059', 'taohong@email.com', '虹姐', 'wx_taohong59', 4, 6, 2, NULL, 1, 2, 1, 2, 2, NULL, 4, '2024-09-20 15:15:00'),
(3, NULL, 2, 4, '闫妮', '13800138060', 'yanni@email.com', '妮妮', 'wx_yanni60', 2, NULL, 1, NULL, NULL, NULL, NULL, NULL, 1, NULL, 1, '2024-09-20 16:50:00');

-- =====================================================
-- 
-- 
-- =====================================================
DROP TABLE IF EXISTS advisor_call_duration_stats;

CREATE TABLE advisor_call_duration_stats (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    advisor_id SMALLINT NOT NULL COMMENT '顾问ID',
    advisor_name VARCHAR(50) NOT NULL COMMENT '顾问姓名',
    stats_date DATE NOT NULL COMMENT '统计日期',
    device_id VARCHAR(50) NOT NULL COMMENT '设备ID',
    
    -- 总体统计
    total_calls BIGINT NOT NULL DEFAULT 0 COMMENT '总呼叫记录数',
    total_connected BIGINT NOT NULL DEFAULT 0 COMMENT '总接通数目',
    total_unconnected BIGINT NOT NULL DEFAULT 0 COMMENT '未接通总数',
    total_duration BIGINT NOT NULL DEFAULT 0 COMMENT '总通话时长(秒)',
    total_duration_correction BIGINT NOT NULL DEFAULT 0 COMMENT '总通话时长修正值(秒)',
    connection_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '接通率(%)',
    
    -- 呼出统计
    outbound_calls BIGINT NOT NULL DEFAULT 0 COMMENT '总呼出记录',
    outbound_connected BIGINT NOT NULL DEFAULT 0 COMMENT '呼出接通数目',
    outbound_unconnected BIGINT NOT NULL DEFAULT 0 COMMENT '呼出未接通数',
    outbound_duration BIGINT NOT NULL DEFAULT 0 COMMENT '呼出总通话时长(秒)',
    outbound_connection_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '呼出接通率(%)',
    
    -- 呼入统计
    inbound_calls BIGINT NOT NULL DEFAULT 0 COMMENT '总呼入记录',
    inbound_connected BIGINT NOT NULL DEFAULT 0 COMMENT '呼入接通数目',
    inbound_unconnected BIGINT NOT NULL DEFAULT 0 COMMENT '呼入未接通数',
    inbound_duration BIGINT NOT NULL DEFAULT 0 COMMENT '呼入总通话时长(秒)',
    inbound_connection_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '呼入接通率(%)',
    
    -- 通话时长分段统计(总体) - 修正字段名匹配API
    duration_under_5s BIGINT NOT NULL DEFAULT 0 COMMENT '通话时长<5秒总数',
    duration_5s_to_10s BIGINT NOT NULL DEFAULT 0 COMMENT '通话时长5-10秒总数',
    duration_10s_to_20s BIGINT NOT NULL DEFAULT 0 COMMENT '通话时长10-20秒总数',
    duration_20s_to_30s BIGINT NOT NULL DEFAULT 0 COMMENT '通话时长20-30秒总数',
    duration_30s_to_45s BIGINT NOT NULL DEFAULT 0 COMMENT '通话时长30-45秒总数',
    duration_45s_to_60s BIGINT NOT NULL DEFAULT 0 COMMENT '通话时长45-60秒总数',
    duration_over_60s BIGINT NOT NULL DEFAULT 0 COMMENT '通话时长大于60秒总数',
    
    -- 呼出通话时长分段统计 - 修正字段名匹配API
    outbound_duration_under_5s BIGINT NOT NULL DEFAULT 0 COMMENT '呼出通话时长<5秒',
    outbound_duration_5s_to_10s BIGINT NOT NULL DEFAULT 0 COMMENT '呼出通话时长5-10秒',
    outbound_duration_10s_to_20s BIGINT NOT NULL DEFAULT 0 COMMENT '呼出通话时长10-20秒',
    outbound_duration_20s_to_30s BIGINT NOT NULL DEFAULT 0 COMMENT '呼出通话时长20-30秒',
    outbound_duration_30s_to_45s BIGINT NOT NULL DEFAULT 0 COMMENT '呼出通话时长30-45秒',
    outbound_duration_45s_to_60s BIGINT NOT NULL DEFAULT 0 COMMENT '呼出通话时长45-60秒',
    outbound_duration_over_60s BIGINT NOT NULL DEFAULT 0 COMMENT '呼出通话时长大于60秒',
    
    -- 呼入通话时长分段统计 - 修正字段名匹配API
    inbound_duration_under_5s BIGINT NOT NULL DEFAULT 0 COMMENT '呼入通话时长<5秒',
    inbound_duration_5s_to_10s BIGINT NOT NULL DEFAULT 0 COMMENT '呼入通话时长5-10秒',
    inbound_duration_10s_to_20s BIGINT NOT NULL DEFAULT 0 COMMENT '呼入通话时长10-20秒',
    inbound_duration_20s_to_30s BIGINT NOT NULL DEFAULT 0 COMMENT '呼入通话时长20-30秒',
    inbound_duration_30s_to_45s BIGINT NOT NULL DEFAULT 0 COMMENT '呼入通话时长30-45秒',
    inbound_duration_45s_to_60s BIGINT NOT NULL DEFAULT 0 COMMENT '呼入通话时长45-60秒',
    inbound_duration_over_60s BIGINT NOT NULL DEFAULT 0 COMMENT '呼入通话时长大于60秒',
    
    -- 指标相关字段
    goal BIGINT NOT NULL DEFAULT 7200 COMMENT '今日指标',
    goal_completed_today BOOLEAN NOT NULL DEFAULT FALSE COMMENT '今天是否完成指标',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE KEY uk_advisor_date (advisor_id, stats_date),
    KEY idx_advisor_id (advisor_id),
    KEY idx_stats_date (stats_date)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='顾问通话时长统计表';

-- 插入顾问通话时长统计数据
INSERT INTO advisor_call_duration_stats (
    advisor_id, advisor_name, stats_date, device_id,
    total_calls, total_connected, total_unconnected, total_duration, total_duration_correction, connection_rate,
    outbound_calls, outbound_connected, outbound_unconnected, outbound_duration, outbound_connection_rate,
    inbound_calls, inbound_connected, inbound_unconnected, inbound_duration, inbound_connection_rate,
    duration_under_5s, duration_5s_to_10s, duration_10s_to_20s, duration_20s_to_30s, 
    duration_30s_to_45s, duration_45s_to_60s, duration_over_60s,
    outbound_duration_under_5s, outbound_duration_5s_to_10s, outbound_duration_10s_to_20s, 
    outbound_duration_20s_to_30s, outbound_duration_30s_to_45s, outbound_duration_45s_to_60s, outbound_duration_over_60s,
    inbound_duration_under_5s, inbound_duration_5s_to_10s, inbound_duration_10s_to_20s, 
    inbound_duration_20s_to_30s, inbound_duration_30s_to_45s, inbound_duration_45s_to_60s, inbound_duration_over_60s
) VALUES
-- 张小明的统计数据 (2024-01-15)
(
    1001, '张小明', '2025-09-25', 'ebt-5b343ab5',
    -- 总体统计
    150, 120, 30, 7200, 0, 80.00,
    -- 呼出统计  
    90, 75, 15, 4500, 83.33,
    -- 呼入统计
    60, 45, 15, 2700, 75.00,
    -- 总体时长分段
    10, 15, 25, 20, 30, 15, 5,
    -- 呼出时长分段
    5, 8, 15, 12, 20, 10, 5,
    -- 呼入时长分段
    5, 7, 10, 8, 10, 5, 0
),
-- 李小红的统计数据 (2024-01-15)
(
    1002, '李小红', '2025-09-25', '8002',
    -- 总体统计
    200, 180, 20, 10800, 0, 90.00,
    -- 呼出统计
    120, 110, 10, 6600, 91.67,
    -- 呼入统计
    80, 70, 10, 4200, 87.50,
    -- 总体时长分段
    8, 12, 30, 35, 45, 35, 15,
    -- 呼出时长分段
    3, 6, 18, 22, 28, 23, 10,
    -- 呼入时长分段
    5, 6, 12, 13, 17, 12, 5
);


DROP TABLE IF EXISTS advisor_device_config;

CREATE TABLE advisor_device_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    device_id VARCHAR(50) NOT NULL COMMENT '设备ID',
    devid VARCHAR(200) COMMENT '设备ID（新字段）',
    advisor_id SMALLINT NOT NULL COMMENT '顾问ID',
    advisor_name VARCHAR(50) NOT NULL COMMENT '顾问姓名',
    goal BIGINT NOT NULL DEFAULT 7200 COMMENT '指标',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    KEY idx_device_id (device_id),
    KEY idx_devid (devid),
    KEY idx_advisor_id (advisor_id),
    
    -- 外键约束
    FOREIGN KEY (advisor_id) REFERENCES advisors(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='顾问设备配置表';

-- 插入顾问设备配置数据
INSERT INTO advisor_device_config (device_id, devid, advisor_id, advisor_name, goal, created_at, updated_at) VALUES
('ebt-5b343ab5', 'ebt-5b343ab5', 1, 'grey', 0, '2025-09-25 18:00:24', '2025-10-08 18:38:21'),
('ebt-c86a2a86', 'ebt-c86a2a86', 2, 'NIKO', 7200, '2025-09-25 18:00:24', '2025-10-08 18:38:23'),
('ebt-ae2f3221', 'ebt-ae2f3221', 3, '俊涛', 7200, '2025-09-26 11:00:36', '2025-10-08 18:38:24'),
('ebt-10d0aea2', 'ebt-10d0aea2', 4, '智浩', 7200, '2025-09-26 11:10:56', '2025-10-08 18:38:25'),
('ebt-106546ad', 'ebt-106546ad', 5, '思怡', 7200, '2025-09-26 11:11:19', '2025-10-08 18:38:26'),
('ebt-f836aa7e', 'ebt-f836aa7e', 6, '佳慧', 7200, '2025-09-26 11:12:00', '2025-10-08 18:38:28');

-- =====================================================
-- 电话待打表
-- =====================================================

DROP TABLE IF EXISTS phone_call_queue;

CREATE TABLE phone_call_queue (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    phone VARCHAR(20) NOT NULL COMMENT '电话号码',
    is_called BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已经拨打：TRUE=已拨打，FALSE=未拨打',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引设计
    INDEX idx_phone (phone),
    INDEX idx_is_called (is_called),
    INDEX idx_created_at (created_at),
    
    -- 唯一约束：防止重复电话号码
    UNIQUE KEY uk_phone (phone)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电话待打表';

-- 插入测试数据
INSERT INTO phone_call_queue (phone, is_called) VALUES
('13800138001', FALSE),
('13800138002', FALSE),
('13800138003', TRUE),
('13800138004', FALSE),
('13800138005', TRUE),
('13800138006', FALSE),
('13800138007', FALSE),
('13800138008', TRUE),
('13800138009', FALSE),
('13800138010', FALSE);