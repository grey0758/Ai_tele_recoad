-- 我需要设置一个顾问通话时长统计表，表名是advisor_call_duration_stats，表结构如下：
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
    advisor_id SMALLINT NOT NULL COMMENT '顾问ID',
    advisor_name VARCHAR(50) NOT NULL COMMENT '顾问姓名',
    goal BIGINT NOT NULL DEFAULT 7200 COMMENT '指标',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    KEY idx_device_id (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='顾问设备配置表';

-- 插入顾问设备配置数据
INSERT INTO advisor_device_config (device_id, advisor_id, advisor_name, daily_goal) VALUES
('8001', 'ebt-5b343ab5', '张小明', 100),
('8002', 1002, '李小红', 150);