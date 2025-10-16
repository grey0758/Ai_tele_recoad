-- 创建定时任务配置表
CREATE TABLE scheduled_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL COMMENT '任务名称',
    task_type VARCHAR(50) NOT NULL COMMENT '任务类型',
    cron_expression VARCHAR(100) NOT NULL COMMENT 'Cron表达式',
    start_time TIME COMMENT '开始时间',
    end_time TIME COMMENT '结束时间',
    interval_minutes INT COMMENT '间隔分钟数',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    description TEXT COMMENT '任务描述',
    last_run DATETIME COMMENT '上次执行时间',
    next_run DATETIME COMMENT '下次执行时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- 任务执行日志表
CREATE TABLE task_execution_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT,
    execution_time DATETIME,
    status ENUM('success', 'failed', 'running') DEFAULT 'running',
    error_message TEXT,
    execution_duration INT COMMENT '执行时长(秒)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(id)
);

-- 插入定时任务配置
INSERT INTO scheduled_tasks (
    task_name, 
    task_type, 
    cron_expression, 
    start_time, 
    end_time, 
    interval_minutes,
    description
) VALUES 
('advisor_call_duration_stats_task', 'data_sync', '*/5 * * * *', '08:59:00', '21:59:00', 60, '每小时执行任务，中午12点暂停');
INSERT INTO scheduled_tasks (
    task_name, 
    task_type, 
    cron_expression, 
    start_time, 
    end_time, 
    interval_minutes,
    description
) VALUES 
('send.advisor.stats.wechat.report.task', 'data_sync_service', '2 10-12,14-22 * * *', '09:01:00', '22:02:00', 60, '数据同步服务，在59分任务执行后的下个小时01分执行，中午13点暂停');
INSERT INTO scheduled_tasks (
    task_name, 
    task_type, 
    cron_expression, 
    start_time, 
    end_time, 
    interval_minutes,
    description
) VALUES 
('generate.advisor.analysis.report.task', 'data_sync_service', '0 6 * * *', '06:00:00', '06:00:00', 1440, '每天六点执行一次顾问分析报告生成任务');