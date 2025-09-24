-- =====================================================
-- 删除所有表的SQL语句
-- 注意：由于存在外键约束，需要按照依赖关系的逆序删除
-- =====================================================
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `lead_status_logs`;
DROP TABLE IF EXISTS `call_records`;
DROP TABLE IF EXISTS `lead2_leads`;
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
-- 验证所有表是否已删除
-- =====================================================
SHOW TABLES;

-- =====================================================
-- 线索类型配置表
-- 用途：管理线索的分类体系，支持二级分类
-- 特点：支持父子级关系，JSON配置灵活扩展
-- =====================================================
CREATE TABLE lead_categories (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '类型名称：如直播、公海、旧线索等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '类型编码：用于程序识别，如LIVE、PUBLIC、OLD',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    config JSON COMMENT '类型配置信息：包含描述、自动分配规则、优先级评分等',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    status TINYINT DEFAULT 1 COMMENT '状态：1=启用，0=禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_status (parent_id, status),
    INDEX idx_code (code),

    -- 外键约束：保证数据完整性（移除COMMENT）
    FOREIGN KEY (parent_id) REFERENCES lead_categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='线索类型配置表';

-- 线索类型表初始化数据
INSERT INTO lead_categories (name, code, parent_id, sort_order) VALUES
('直播', 'LIVE', NULL, 1),
('短视频线索', 'SHORT_VIDEO', NULL, 2),
('公海', 'PUBLIC', NULL, 3);

-- 获取直播的ID，用于创建子分类
SET @live_id = (SELECT id FROM lead_categories WHERE code = 'LIVE');

-- 直播的子分类
INSERT INTO lead_categories (name, code, parent_id, sort_order) VALUES
('直播间1', 'LIVE_ROOM_1', @live_id, 1),
('直播间2', 'LIVE_ROOM_2', @live_id, 2);

-- =====================================================
-- 电话状态表
-- 用途：管理电话呼叫的各种状态
-- 特点：支持二级分类，如已接听下的有需求/没有需求
-- =====================================================
CREATE TABLE call_status (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '状态名称：如未联系、空号、未接听、已接听等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '状态编码：用于程序识别，如UNCONTACTED、EMPTY、UNANSWERED、ANSWERED',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    config JSON COMMENT '状态配置信息：包含描述、后续动作、统计权重等',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    status TINYINT DEFAULT 1 COMMENT '状态：1=启用，0=禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_status (parent_id, status),
    INDEX idx_code (code),

    -- 外键约束：保证数据完整性
    FOREIGN KEY (parent_id) REFERENCES call_status(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电话状态表';

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

-- =====================================================
-- 微信状态表
-- 用途：管理微信添加状态
-- =====================================================
CREATE TABLE wechat_status (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '状态名称：如未添加、已添加等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '状态编码：用于程序识别，如NOT_ADDED、ADDED',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    config JSON COMMENT '状态配置信息：包含描述、后续动作、统计权重等',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    status TINYINT DEFAULT 1 COMMENT '状态：1=启用，0=禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_status (parent_id, status),
    INDEX idx_code (code),

    -- 外键约束：保证数据完整性
    FOREIGN KEY (parent_id) REFERENCES wechat_status(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='微信状态表';

-- 初始化数据
INSERT INTO wechat_status (name, code, parent_id, sort_order) VALUES
('未添加', 'NOT_ADDED', NULL, 1),
('已添加', 'ADDED', NULL, 2);

-- =====================================================
-- 私域回看状态表
-- =====================================================
CREATE TABLE `private_domain_review_status` (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '状态ID',
    parent_id TINYINT DEFAULT NULL COMMENT '父级状态ID，用于层级关系',
    status_code VARCHAR(30) UNIQUE NOT NULL COMMENT '状态代码：唯一标识',
    status_name VARCHAR(50) NOT NULL COMMENT '状态名称：显示名称',
    status_description VARCHAR(200) COMMENT '状态描述：详细说明',
    sort_order TINYINT DEFAULT 0 COMMENT '排序权重：数字越小越靠前',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用：控制状态可用性',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_parent_sort (parent_id, sort_order),
    INDEX idx_status_code (status_code),
    INDEX idx_active_sort (is_active, sort_order),
    FOREIGN KEY (parent_id) REFERENCES private_domain_review_status(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='私域回看状态表';

-- 初始化私域回看状态数据
INSERT INTO `private_domain_review_status` (id, parent_id, status_code, status_name, status_description, sort_order) VALUES
-- 主状态
(1, NULL, 'SENT_TO_PRIVATE', '发私域', '已发送到私域', 1),

-- 发私域的子状态
(2, 1, 'NOT_VIEWED_REVIEW', '未看回看', '已发私域但未观看回看内容', 1),
(3, 1, 'VIEWED_REVIEW', '已看回看', '已发私域且已观看回看内容', 2);

-- =====================================================
-- 私域参加状态表
-- =====================================================
CREATE TABLE `private_domain_participation_status` (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '状态ID',
    parent_id TINYINT DEFAULT NULL COMMENT '父级状态ID，用于层级关系',
    status_code VARCHAR(30) UNIQUE NOT NULL COMMENT '状态代码：唯一标识',
    status_name VARCHAR(50) NOT NULL COMMENT '状态名称：显示名称',
    status_description VARCHAR(200) COMMENT '状态描述：详细说明',
    sort_order TINYINT DEFAULT 0 COMMENT '排序权重：数字越小越靠前',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用：控制状态可用性',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_parent_sort (parent_id, sort_order),
    INDEX idx_status_code (status_code),
    INDEX idx_active_sort (is_active, sort_order),
    FOREIGN KEY (parent_id) REFERENCES private_domain_participation_status(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='私域参加状态表';

-- 初始化私域参加状态数据
INSERT INTO `private_domain_participation_status` (id, parent_id, status_code, status_name, status_description, sort_order) VALUES
-- 主状态
(1, NULL, 'PARTICIPATION', '参加私域', '私域参加相关状态', 1),

-- 参加私域的子状态
(2, 1, 'NOT_PARTICIPATED', '未参加', '未参加私域活动', 1),
(3, 1, 'PARTICIPATED', '已经参加', '已经参加私域活动', 2);

-- =====================================================
-- 日程状态表
-- 用途：管理日程预约状态
-- =====================================================
CREATE TABLE schedule_status (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '状态名称：如未约日程、已约日程等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '状态编码：用于程序识别',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    config JSON COMMENT '状态配置信息：包含描述、后续动作、统计权重等',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    status TINYINT DEFAULT 1 COMMENT '状态：1=启用，0=禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_status (parent_id, status),
    INDEX idx_code (code),

    -- 外键约束：保证数据完整性
    FOREIGN KEY (parent_id) REFERENCES schedule_status(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日程状态表';

-- 初始化数据
INSERT INTO schedule_status (name, code, parent_id, sort_order) VALUES
('未约日程', 'NOT_SCHEDULED', NULL, 1),
('已约日程', 'SCHEDULED', NULL, 2);

-- =====================================================
-- 合同状态表
-- 用途：管理合同签署流程状态
-- =====================================================
CREATE TABLE contract_status (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '状态名称：如未拉群、已经拉群、已签合同、已收款等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '状态编码：用于程序识别',
    parent_id TINYINT DEFAULT NULL COMMENT '父级ID，NULL表示一级分类，有值表示二级分类',
    config JSON COMMENT '状态配置信息：包含描述、后续动作、统计权重等',
    sort_order TINYINT DEFAULT 0 COMMENT '排序字段：数字越小越靠前',
    status TINYINT DEFAULT 1 COMMENT '状态：1=启用，0=禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计：优化查询性能
    INDEX idx_parent_status (parent_id, status),
    INDEX idx_code (code),

    -- 外键约束：保证数据完整性
    FOREIGN KEY (parent_id) REFERENCES contract_status(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='合同状态表';

-- 初始化数据
INSERT INTO contract_status (name, code, parent_id, sort_order) VALUES
('未拉群', 'NOT_GROUPED', NULL, 1),
('已经拉群', 'GROUPED', NULL, 2),
('已签合同', 'CONTRACT_SIGNED', NULL, 3),
('已收款', 'PAYMENT_RECEIVED', NULL, 4);


-- =====================================================
-- 顾问组表
-- 用途：管理销售顾问的组织架构
-- 特点：支持组级别的配置和管理
-- =====================================================
CREATE TABLE advisor_groups (
    id TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(30) NOT NULL COMMENT '组名：如一号组、二号组等',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '组编码：用于程序识别',
    leader_id SMALLINT COMMENT '组长ID：关联advisors表，但不设外键避免循环依赖',
    lead_category_id TINYINT COMMENT '线索类型ID：关联lead_categories表，指定该组负责的线索类型',
    settings JSON COMMENT '组设置：工作时间、分配规则、最大线索数等配置信息',
    status TINYINT DEFAULT 1 COMMENT '状态：1=启用，0=禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引设计
    INDEX idx_code (code),
    INDEX idx_status (status),
    INDEX idx_lead_category (lead_category_id),

    -- 外键约束
    FOREIGN KEY (lead_category_id) REFERENCES lead_categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='顾问组表';

INSERT INTO advisor_groups (name, code) VALUES
('一号组', 'GROUP_1'),
('二号组', 'GROUP_2'),
('三号组', 'GROUP_3');

-- =====================================================
-- 顾问表
-- 用途：管理销售顾问的基本信息和工作配置
-- 特点：JSON字段存储灵活的配置和统计信息
-- =====================================================
DROP TABLE IF EXISTS `advisors`;

CREATE TABLE `advisors`  (
  `id` SMALLINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `group_id` TINYINT NOT NULL COMMENT '所属组ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '顾问姓名',
  `employee_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '工号：唯一标识',
  `contact_info` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '联系方式：包含phone、email、wechat等字段',
  `work_config` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '工作配置：最大线索数、工作时间、专长领域等',
  `performance_stats` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '绩效统计：转化率、响应时间、客户满意度等实时统计',
  `status` tinyint NULL DEFAULT 1 COMMENT '状态：1=在职，0=离职，2=休假',
  `created_at` timestamp NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `employee_no`(`employee_no` ASC) USING BTREE,
  INDEX `idx_group_status`(`group_id` ASC, `status` ASC) USING BTREE,
  INDEX `idx_employee_no`(`employee_no` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE
--   CONSTRAINT `advisors_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `advisor_groups` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '顾问表' ROW_FORMAT = Dynamic;

INSERT INTO advisors (group_id, name, employee_no, status) VALUES
(1, '张三', 'EMP001', 1),
(1, '李四', 'EMP002', 1),
(2, '王五', 'EMP003', 1),
(2, '赵六', 'EMP004', 1),
(3, '孙七', 'EMP005', 1),
(3, '周八', 'EMP006', 1);

-- =====================================================
-- 线索主表
-- 用途：存储所有线索的完整信息
-- 设计理念：核心字段关系型，扩展信息JSON化
-- =====================================================

DROP TABLE IF EXISTS `lead2_leads`;

CREATE TABLE `lead2_leads` (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID，使用BIGINT支持大数据量',
    lead_no VARCHAR(30) UNIQUE NOT NULL COMMENT '线索编号：业务唯一标识，格式如LEAD20240917001',

    -- 核心分类信息
    category_id TINYINT NOT NULL COMMENT '线索类型ID：关联lead_categories表',
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

    -- 🎯 状态字段（主状态+子状态设计）
    call_status_id TINYINT COMMENT '电话主状态ID：关联call_status表',
    call_sub_status_id TINYINT COMMENT '电话子状态ID：关联call_status表的二级分类',
    
    wechat_status_id TINYINT COMMENT '微信主状态ID：关联wechat_status表',
    wechat_sub_status_id TINYINT COMMENT '微信子状态ID：关联wechat_status表的二级分类',
    
    -- 🆕 两个独立的私域状态
    private_domain_review_status_id TINYINT COMMENT '私域回看主状态ID：关联private_domain_review_status表',
    private_domain_review_sub_status_id TINYINT COMMENT '私域回看子状态ID：关联private_domain_review_status表的二级分类',
    
    private_domain_participation_status_id TINYINT COMMENT '私域参加主状态ID：关联private_domain_participation_status表',
    private_domain_participation_sub_status_id TINYINT COMMENT '私域参加子状态ID：关联private_domain_participation_status表的二级分类',
    
    schedule_status_id TINYINT COMMENT '日程主状态ID：关联schedule_status表',
    schedule_sub_status_id TINYINT COMMENT '日程子状态ID：关联schedule_status表的二级分类',
    schedule_times TINYINT DEFAULT 0 COMMENT '日程次数',
    
    contract_status_id TINYINT COMMENT '合同主状态ID：关联contract_status表',
    contract_sub_status_id TINYINT COMMENT '合同子状态ID：关联contract_status表的二级分类',

    -- 分析字段
    analysis_failed_records TINYINT DEFAULT 0 COMMENT '未能联系次数',
    last_contact_record_id BIGINT COMMENT '最后一次可联系通话ID',
    last_contact_time TIMESTAMP COMMENT '最后一次可联系时间',
    last_analysis_failed_record_id BIGINT COMMENT '最后一次未能联系通话ID',
    last_analysis_failed_time TIMESTAMP COMMENT '最后一次未能联系时间',

    -- 时间字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 外键约束（数据类型已匹配）
    FOREIGN KEY (category_id) REFERENCES lead_categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (sub_category_id) REFERENCES lead_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (advisor_group_id) REFERENCES advisor_groups(id) ON DELETE SET NULL,
    FOREIGN KEY (advisor_id) REFERENCES advisors(id) ON DELETE SET NULL,
    
    -- 状态表外键约束（TINYINT匹配TINYINT）
    FOREIGN KEY (call_status_id) REFERENCES call_status(id) ON DELETE SET NULL,
    FOREIGN KEY (call_sub_status_id) REFERENCES call_status(id) ON DELETE SET NULL,
    
    FOREIGN KEY (wechat_status_id) REFERENCES wechat_status(id) ON DELETE SET NULL,
    FOREIGN KEY (wechat_sub_status_id) REFERENCES wechat_status(id) ON DELETE SET NULL,
    
    -- 🆕 两个独立私域状态的外键约束（TINYINT匹配TINYINT）
    FOREIGN KEY (private_domain_review_status_id) REFERENCES private_domain_review_status(id) ON DELETE SET NULL,
    FOREIGN KEY (private_domain_review_sub_status_id) REFERENCES private_domain_review_status(id) ON DELETE SET NULL,
    
    FOREIGN KEY (private_domain_participation_status_id) REFERENCES private_domain_participation_status(id) ON DELETE SET NULL,
    FOREIGN KEY (private_domain_participation_sub_status_id) REFERENCES private_domain_participation_status(id) ON DELETE SET NULL,
    
    FOREIGN KEY (schedule_status_id) REFERENCES schedule_status(id) ON DELETE SET NULL,
    FOREIGN KEY (schedule_sub_status_id) REFERENCES schedule_status(id) ON DELETE SET NULL,
    
    FOREIGN KEY (contract_status_id) REFERENCES contract_status(id) ON DELETE SET NULL,
    FOREIGN KEY (contract_sub_status_id) REFERENCES contract_status(id) ON DELETE SET NULL,

    -- 🚀 性能优化索引
    INDEX idx_category_advisor (category_id, advisor_id),
    INDEX idx_advisor_status (advisor_id, call_status_id),
    INDEX idx_phone (customer_phone),
    INDEX idx_created_category (created_at, category_id),
    INDEX idx_status_combination (call_status_id, wechat_status_id, schedule_status_id)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='线索主表-系统核心业务表（独立私域状态设计）';

-- 第1-10条：直播线索
('LEAD20240917001', 1, 2, 1, 1, '陈小明', '13800138001', 'chenxm@email.com', '阳光小陈', 'wx_chenxm01', 4, 6, 2, 1, 2, 1, 2, 2, 1, 0, 1, '2024-09-17 08:30:00'),
('LEAD20240917002', 1, 2, 1, 2, '刘美丽', '13800138002', 'liuml@email.com', '美丽人生', 'wx_liuml02', 4, 6, 2, 1, 3, 1, 3, 2, 2, 0, 1, '2024-09-17 09:15:00'),
('LEAD20240917003', 1, 3, 2, 3, '王大力', '13800138003', 'wangdl@email.com', '大力水手', 'wx_wangdl03', 3, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 2, 0, '2024-09-17 10:20:00'),
('LEAD20240917004', 1, 2, 1, 1, '李小花', '13800138004', 'lixh@email.com', '花花世界', 'wx_lixh04', 4, 5, 2, 1, 2, 1, 2, 1, 1, 0, 0, '2024-09-17 11:45:00'),
('LEAD20240917005', 1, 3, 2, 4, '张强', '13800138005', 'zhangq@email.com', '强哥在线', 'wx_zhangq05', 2, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 1, 0, '2024-09-17 13:10:00'),
('LEAD20240917006', 1, 2, 3, 5, '赵敏', '13800138006', 'zhaomin@email.com', '敏敏特穆尔', 'wx_zhaomin06', 4, 6, 2, 1, 3, 1, 3, 2, 3, 0, 2, '2024-09-17 14:30:00'),
('LEAD20240917007', 1, 3, 1, 2, '孙悟空', '13800138007', 'sunwk@email.com', '齐天大圣', 'wx_sunwk07', 1, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 0, 0, '2024-09-17 15:45:00'),
('LEAD20240917008', 1, 2, 2, 3, '周杰伦', '13800138008', 'zhoujl@email.com', '周董', 'wx_zhoujl08', 4, 6, 2, 1, 2, 1, 2, 2, 2, 0, 1, '2024-09-17 16:20:00'),
('LEAD20240917009', 1, 3, 3, 6, '林志玲', '13800138009', 'linzl@email.com', '志玲姐姐', 'wx_linzl09', 3, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 1, 0, '2024-09-17 17:15:00'),
('LEAD20240917010', 1, 2, 1, 1, '马云', '13800138010', 'mayun@email.com', '风清扬', 'wx_mayun10', 4, 5, 2, 1, 3, 1, 3, 1, 1, 0, 0, '2024-09-17 18:30:00'),

-- 第11-20条：短视频线索
('LEAD20240918011', 2, NULL, 2, 4, '刘德华', '13800138011', 'liudh@email.com', '华仔', 'wx_liudh11', 4, 6, 2, 1, 2, 1, 2, 2, 4, 0, 3, '2024-09-18 08:45:00'),
('LEAD20240918012', 2, NULL, 1, 2, '张学友', '13800138012', 'zhangxy@email.com', '歌神', 'wx_zhangxy12', 3, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 2, 0, '2024-09-18 09:30:00'),
('LEAD20240918013', 2, NULL, 3, 5, '郭富城', '13800138013', 'guofc@email.com', '城城', 'wx_guofc13', 4, 5, 2, 1, 3, 1, 3, 2, 1, 0, 1, '2024-09-18 10:15:00'),
('LEAD20240918014', 2, NULL, 2, 3, '黎明', '13800138014', 'liming@email.com', '黎天王', 'wx_liming14', 2, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 1, 0, '2024-09-18 11:20:00'),
('LEAD20240918015', 2, NULL, 1, 1, '梁朝伟', '13800138015', 'liangcw@email.com', '伟仔', 'wx_liangcw15', 4, 6, 2, 1, 2, 1, 2, 2, 2, 0, 2, '2024-09-18 12:45:00'),
('LEAD20240918016', 2, NULL, 3, 6, '周星驰', '13800138016', 'zhouxc@email.com', '星爷', 'wx_zhouxc16', 1, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 0, 0, '2024-09-18 13:30:00'),
('LEAD20240918017', 2, NULL, 2, 4, '成龙', '13800138017', 'chenglong@email.com', '大哥', 'wx_chenglong17', 4, 5, 2, 1, 3, 1, 3, 1, 1, 0, 0, '2024-09-18 14:15:00'),
('LEAD20240918018', 2, NULL, 1, 2, '李连杰', '13800138018', 'lilj@email.com', '李师傅', 'wx_lilj18', 3, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 3, 0, '2024-09-18 15:45:00'),
('LEAD20240918019', 2, NULL, 3, 5, '甄子丹', '13800138019', 'zhenzd@email.com', '丹爷', 'wx_zhenzd19', 4, 6, 2, 1, 2, 1, 2, 2, 3, 0, 1, '2024-09-18 16:30:00'),
('LEAD20240918020', 2, NULL, 2, 3, '吴京', '13800138020', 'wujing@email.com', '京哥', 'wx_wujing20', 4, 5, 2, 1, 3, 1, 3, 2, 2, 0, 2, '2024-09-18 17:20:00'),

-- 第21-31条：公海线索
('LEAD20240919021', 3, NULL, 1, 1, '范冰冰', '13800138021', 'fanbb@email.com', '冰冰', 'wx_fanbb21', 2, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 1, 0, '2024-09-19 08:20:00'),
('LEAD20240919022', 3, NULL, 2, 4, '章子怡', '13800138022', 'zhangzy@email.com', '子怡', 'wx_zhangzy22', 4, 6, 2, 1, 2, 1, 2, 2, 1, 0, 1, '2024-09-19 09:45:00'),
('LEAD20240919023', 3, NULL, 3, 6, '赵薇', '13800138023', 'zhaowei@email.com', '小燕子', 'wx_zhaowei23', 3, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 2, 0, '2024-09-19 10:30:00'),
('LEAD20240919024', 3, NULL, 1, 2, '周迅', '13800138024', 'zhouxun@email.com', '迅哥', 'wx_zhouxun24', 4, 5, 2, 1, 3, 1, 3, 1, 1, 0, 0, '2024-09-19 11:15:00'),
('LEAD20240919025', 3, NULL, 2, 3, '徐静蕾', '13800138025', 'xujl@email.com', '老徐', 'wx_xujl25', 1, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 0, 0, '2024-09-19 12:40:00'),
('LEAD20240919026', 3, NULL, 3, 5, '舒淇', '13800138026', 'shuqi@email.com', '淇淇', 'wx_shuqi26', 4, 6, 2, 1, 2, 1, 2, 2, 4, 0, 3, '2024-09-19 13:25:00'),
('LEAD20240919027', 3, NULL, 1, 1, '林心如', '13800138027', 'linxr@email.com', '紫薇', 'wx_linxr27', 4, 5, 2, 1, 3, 1, 3, 2, 2, 0, 1, '2024-09-19 14:50:00'),
('LEAD20240919028', 3, NULL, 2, 4, '杨幂', '13800138028', 'yangmi@email.com', '大幂幂', 'wx_yangmi28', 3, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 1, 0, '2024-09-19 15:35:00'),
('LEAD20240919029', 3, NULL, 3, 6, '刘诗诗', '13800138029', 'liuss@email.com', '诗诗', 'wx_liuss29', 4, 6, 2, 1, 2, 1, 2, 2, 3, 0, 2, '2024-09-19 16:20:00'),
('LEAD20240919030', 3, NULL, 1, 2, '唐嫣', '13800138030', 'tangyan@email.com', '糖糖', 'wx_tangyan30', 2, NULL, 1, NULL, NULL, NULL, NULL, 1, 1, 1, 0, '2024-09-19 17:10:00'),
('LEAD20240919031', 3, NULL, 2, 3, '高圆圆', '13800138031', 'gaoyy@email.com', '圆圆', 'wx_gaoyy31', 4, 5, 2, 1, 3, 1, 3, 1, 1, 0, 0, '2024-09-19 18:45:00');

-- =====================================================
-- 通话记录表
-- 用途：记录所有通话信息，包括录音、状态转换、对话内容等
-- 特点：与线索表关联，支持客户状态变更追踪
-- =====================================================
CREATE TABLE call_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID，使用BIGINT支持大数据量',
    call_no VARCHAR(30) UNIQUE NOT NULL COMMENT '通话编号：业务唯一标识，格式如CALL20240917001',
    
    -- 关联信息
    lead_id BIGINT NOT NULL COMMENT '关联的线索ID',
    advisor_id SMALLINT NOT NULL COMMENT '通话顾问ID',
    
    -- 通话基础信息
    call_type ENUM('INBOUND', 'INBOUND_MISSED', 'OUTBOUND', 'OUTBOUND_MISSED') 
              NOT NULL COMMENT '通话类型：呼入、呼入未接、呼出、呼出未接',
    caller_phone VARCHAR(20) NOT NULL COMMENT '主叫号码',
    callee_phone VARCHAR(20) NOT NULL COMMENT '被叫号码',
    
    -- 通话详情
    call_duration SMALLINT DEFAULT 0 COMMENT '通话时长（秒）：0表示未接通',
    start_time TIMESTAMP NOT NULL COMMENT '通话开始时间',
    end_time TIMESTAMP COMMENT '通话结束时间',
    
    -- 录音信息
    recording_url VARCHAR(300) COMMENT '录音文件URL地址',
    recording_duration SMALLINT COMMENT '录音时长（秒）',
    recording_status ENUM('RECORDING', 'COMPLETED', 'FAILED', 'DELETED') 
                     DEFAULT 'RECORDING' COMMENT '录音状态：录音中、已完成、失败、已删除',
    -- 对话记录和总结
    conversation_content JSON COMMENT '对话记录：包含对话内容、关键信息提取、客户需求等',
    call_summary TEXT COMMENT '通话总结：顾问填写的通话要点和后续跟进计划',
    
    -- 质量评估
    call_quality_score TINYINT COMMENT '通话质量评分：1-100分，用于质检评估',
    quality_notes TEXT COMMENT '质检备注：质检人员的评价和建议',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    
    -- 外键约束
    FOREIGN KEY (lead_id) REFERENCES lead2_leads(id) ON DELETE CASCADE,
    FOREIGN KEY (advisor_id) REFERENCES advisors(id) ON DELETE RESTRICT,
    
    -- 🚀 性能优化索引
    INDEX idx_lead_time (lead_id, start_time),
    INDEX idx_advisor_time (advisor_id, start_time),
    INDEX idx_call_type_time (call_type, start_time),
    INDEX idx_recording_status (recording_status),
    INDEX idx_phone_time (caller_phone, start_time)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通话记录表-记录所有通话详情和状态变更';

-- =====================================================
-- 线索状态变更日志表（简化版）
-- 用途：记录线索状态变更历史和操作人
-- =====================================================
CREATE TABLE lead_status_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    
    -- 关联信息
    lead_id BIGINT NOT NULL COMMENT '线索ID',
    advisor_id SMALLINT COMMENT '操作顾问ID',
    
    -- 状态变更信息
    status_field VARCHAR(50) NOT NULL COMMENT '状态字段名：如call_status_id, wechat_status_id等',
    old_value TINYINT COMMENT '变更前的值',
    new_value TINYINT COMMENT '变更后的值',
    sub_status_field VARCHAR(50) COMMENT '子状态字段名：如call_status_id, wechat_status_id等',
    sub_old_value TINYINT COMMENT '变更前的子状态值',
    sub_new_value TINYINT COMMENT '变更后的子状态值',
    operation_description TEXT COMMENT '操作描述',
    notes TEXT COMMENT '备注',
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '变更时间',
    
    -- 外键约束
    FOREIGN KEY (lead_id) REFERENCES lead2_leads(id) ON DELETE CASCADE,
    FOREIGN KEY (advisor_id) REFERENCES advisors(id) ON DELETE SET NULL,
    
    -- 索引
    INDEX idx_lead_time (lead_id, created_at),
    INDEX idx_advisor_time (advisor_id, created_at),
    INDEX idx_status_field (status_field)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='线索状态变更日志表';

