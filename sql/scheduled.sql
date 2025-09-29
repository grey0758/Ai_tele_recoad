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

-- 插入单个定时任务配置（中午暂停）
INSERT INTO scheduled_tasks (
    task_name, 
    task_type, 
    cron_expression, 
    start_time, 
    end_time, 
    interval_minutes,
    description
) VALUES 
('hourly_task_with_break', 'data_sync', '59 8-12,14-17 * * *', '08:59:00', '17:59:00', 60, '每小时执行任务，中午13点暂停');
INSERT INTO scheduled_tasks (
    task_name, 
    task_type, 
    cron_expression, 
    start_time, 
    end_time, 
    interval_minutes,
    description
) VALUES 
('data_sync_service', 'data_sync', '1 9-12,14-18 * * *', '09:01:00', '18:01:00', 60, '数据同步服务，在59分任务执行后的下个小时01分执行，中午13点暂停');