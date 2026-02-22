-- 飞书AI助手数据库初始化脚本
-- 创建时间: 2026-02-22

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feishu_user_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    avatar_url TEXT,
    department VARCHAR(200),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建日历事件表
CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feishu_event_id VARCHAR(100) UNIQUE NOT NULL,
    calendar_id VARCHAR(100) NOT NULL,
    summary TEXT NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    location TEXT,
    organizer_id VARCHAR(100),
    status VARCHAR(50) DEFAULT 'confirmed',
    event_type VARCHAR(50) DEFAULT 'meeting',
    priority INTEGER DEFAULT 3, -- 1: 高, 2: 中, 3: 低
    is_recurring BOOLEAN DEFAULT false,
    recurrence_rule TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_organizer FOREIGN KEY (organizer_id) REFERENCES users(feishu_user_id) ON DELETE SET NULL
);

-- 创建任务表
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feishu_task_id VARCHAR(100) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    assignee_id VARCHAR(100),
    creator_id VARCHAR(100) NOT NULL,
    due_time TIMESTAMP WITH TIME ZONE,
    completed_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'todo', -- todo, in_progress, done, cancelled
    priority INTEGER DEFAULT 3, -- 1: 紧急, 2: 高, 3: 中, 4: 低
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2),
    tags TEXT[],
    project_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_assignee FOREIGN KEY (assignee_id) REFERENCES users(feishu_user_id) ON DELETE SET NULL,
    CONSTRAINT fk_creator FOREIGN KEY (creator_id) REFERENCES users(feishu_user_id) ON DELETE CASCADE
);

-- 创建消息日志表
CREATE TABLE IF NOT EXISTS message_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feishu_message_id VARCHAR(100) UNIQUE NOT NULL,
    chat_id VARCHAR(100) NOT NULL,
    sender_id VARCHAR(100) NOT NULL,
    message_type VARCHAR(50) NOT NULL, -- text, image, file, etc.
    content TEXT,
    attachments JSONB,
    is_bot_message BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sender FOREIGN KEY (sender_id) REFERENCES users(feishu_user_id) ON DELETE CASCADE
);

-- 创建文档表
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feishu_doc_id VARCHAR(100) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- doc, sheet, bitable, etc.
    owner_id VARCHAR(100) NOT NULL,
    url TEXT,
    last_modified TIMESTAMP WITH TIME ZONE,
    size_bytes BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_owner FOREIGN KEY (owner_id) REFERENCES users(feishu_user_id) ON DELETE CASCADE
);

-- 创建系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    log_level VARCHAR(20) NOT NULL, -- debug, info, warning, error
    module VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    user_id VARCHAR(100),
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(feishu_user_id) ON DELETE SET NULL
);

-- 创建API调用统计表
CREATE TABLE IF NOT EXISTS api_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER NOT NULL,
    user_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(feishu_user_id) ON DELETE SET NULL
);

-- 创建缓存表
CREATE TABLE IF NOT EXISTS cache_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(500) UNIQUE NOT NULL,
    cache_value JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_calendar_events_start_time ON calendar_events(start_time);
CREATE INDEX IF NOT EXISTS idx_calendar_events_calendar_id ON calendar_events(calendar_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_priority ON calendar_events(priority);

CREATE INDEX IF NOT EXISTS idx_tasks_due_time ON tasks(due_time);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee_id ON tasks(assignee_id);

CREATE INDEX IF NOT EXISTS idx_message_logs_chat_id ON message_logs(chat_id);
CREATE INDEX IF NOT EXISTS idx_message_logs_sender_id ON message_logs(sender_id);
CREATE INDEX IF NOT EXISTS idx_message_logs_created_at ON message_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_documents_owner_id ON documents(owner_id);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type);

CREATE INDEX IF NOT EXISTS idx_system_logs_log_level ON system_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_api_stats_endpoint ON api_stats(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_stats_created_at ON api_stats(created_at);

CREATE INDEX IF NOT EXISTS idx_cache_data_expires_at ON cache_data(expires_at);
CREATE INDEX IF NOT EXISTS idx_cache_data_cache_key ON cache_data(cache_key);

-- 创建函数和触发器来更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要updated_at的表创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_calendar_events_updated_at BEFORE UPDATE ON calendar_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入初始数据（可选）
-- INSERT INTO users (feishu_user_id, name, email) VALUES 
-- ('system', '系统用户', 'system@feishu-ai-assistant.com');

-- 创建视图用于常用查询
CREATE OR REPLACE VIEW vw_today_events AS
SELECT 
    ce.*,
    u.name as organizer_name
FROM calendar_events ce
LEFT JOIN users u ON ce.organizer_id = u.feishu_user_id
WHERE DATE(ce.start_time) = CURRENT_DATE
ORDER BY ce.start_time;

CREATE OR REPLACE VIEW vw_overdue_tasks AS
SELECT 
    t.*,
    u.name as assignee_name
FROM tasks t
LEFT JOIN users u ON t.assignee_id = u.feishu_user_id
WHERE t.status != 'done' 
AND t.due_time < CURRENT_TIMESTAMP
ORDER BY t.priority, t.due_time;

CREATE OR REPLACE VIEW vw_api_performance AS
SELECT 
    endpoint,
    method,
    COUNT(*) as total_calls,
    AVG(response_time_ms) as avg_response_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
FROM api_stats
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY endpoint, method
ORDER BY total_calls DESC;

-- 注释
COMMENT ON TABLE users IS '用户信息表';
COMMENT ON TABLE calendar_events IS '日历事件表';
COMMENT ON TABLE tasks IS '任务管理表';
COMMENT ON TABLE message_logs IS '消息日志表';
COMMENT ON TABLE documents IS '文档管理表';
COMMENT ON TABLE system_logs IS '系统日志表';
COMMENT ON TABLE api_stats IS 'API调用统计表';
COMMENT ON TABLE cache_data IS '缓存数据表';

-- 授予权限（在生产环境中需要根据实际情况调整）
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO feishu_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO feishu_app_user;