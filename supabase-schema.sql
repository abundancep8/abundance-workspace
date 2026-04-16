-- Supabase Schema for Agent Memory + Task Logging + Learning Cycles
-- Run this in Supabase SQL Editor to create all tables

-- 1. Agent Memory Table
CREATE TABLE IF NOT EXISTS agent_memory (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  session_id VARCHAR(255) NOT NULL,
  memory_type VARCHAR(50) NOT NULL, -- 'decision', 'pattern', 'insight', 'error', 'optimization'
  content TEXT NOT NULL,
  metadata JSONB, -- Additional context (e.g., {"model": "claude", "tokens": 5000})
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agent_memory_session ON agent_memory(session_id);
CREATE INDEX idx_agent_memory_type ON agent_memory(memory_type);
CREATE INDEX idx_agent_memory_created ON agent_memory(created_at DESC);

-- 2. Task Log Table
CREATE TABLE IF NOT EXISTS task_log (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  task_name VARCHAR(255) NOT NULL,
  model_used VARCHAR(50) NOT NULL, -- 'claude-haiku', 'claude-opus', 'kimi-k2-5', 'gemini-2-flash'
  tokens_used INT NOT NULL,
  cost DECIMAL(10, 4) NOT NULL, -- USD cost
  duration_ms INT NOT NULL, -- Milliseconds to complete
  status VARCHAR(50) NOT NULL, -- 'success', 'error', 'timeout'
  error_message TEXT, -- If failed, error details
  metadata JSONB, -- {"input_tokens": 1000, "output_tokens": 500, "cache_hits": 2}
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_task_log_model ON task_log(model_used);
CREATE INDEX idx_task_log_status ON task_log(status);
CREATE INDEX idx_task_log_created ON task_log(created_at DESC);
CREATE INDEX idx_task_log_cost ON task_log(cost DESC);

-- 3. Learning Cycles Table
CREATE TABLE IF NOT EXISTS learning_cycles (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  cycle_date DATE NOT NULL UNIQUE,
  total_tasks INT DEFAULT 0,
  total_tokens INT DEFAULT 0,
  total_cost DECIMAL(10, 4) DEFAULT 0.0,
  improvements JSONB, -- [{"title": "Use cache for X", "savings": 500}, ...]
  token_savings DECIMAL(10, 4) DEFAULT 0.0, -- Tokens saved vs baseline
  cost_savings DECIMAL(10, 4) DEFAULT 0.0, -- USD saved
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_learning_cycles_date ON learning_cycles(cycle_date DESC);

-- 4. Performance Metrics Table (Real-Time Dashboard)
CREATE TABLE IF NOT EXISTS performance_metrics (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  metric_type VARCHAR(50) NOT NULL, -- 'kimi_savings', 'cache_hit_rate', 'avg_latency', 'cost_per_task'
  metric_value DECIMAL(15, 4) NOT NULL,
  period VARCHAR(50) NOT NULL, -- 'last_hour', 'last_day', 'last_week', 'last_month'
  details JSONB, -- Extra context
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_perf_metrics_type ON performance_metrics(metric_type);
CREATE INDEX idx_perf_metrics_period ON performance_metrics(period);
CREATE INDEX idx_perf_metrics_created ON performance_metrics(created_at DESC);

-- 5. Dashboard Configuration Table
CREATE TABLE IF NOT EXISTS dashboard_config (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  config_key VARCHAR(255) NOT NULL UNIQUE,
  config_value JSONB NOT NULL,
  description TEXT,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO dashboard_config (config_key, config_value, description) VALUES
  ('dashboard_title', '"Agent Performance Dashboard"', 'Title shown on live dashboard'),
  ('refresh_interval_ms', '5000', 'How often dashboard fetches new data (milliseconds)'),
  ('show_kimi_savings', 'true', 'Display Kimi cost savings widget'),
  ('show_token_metrics', 'true', 'Display token usage breakdown'),
  ('cost_threshold_alert', '10.0', 'Alert if daily cost exceeds $X')
ON CONFLICT (config_key) DO NOTHING;

-- 6. Credentials/Secrets Table (Optional - if storing encrypted in DB)
-- NOTE: Not recommended. Use .env files instead. This is just for reference.
CREATE TABLE IF NOT EXISTS credentials_encrypted (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  credential_key VARCHAR(255) NOT NULL UNIQUE,
  encrypted_value TEXT NOT NULL, -- Base64-encoded encrypted value
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS) for task_log if making dashboard public
ALTER TABLE task_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_cycles ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;

-- Public policy for task_log (anyone can read, only app can write)
CREATE POLICY task_log_read ON task_log
  FOR SELECT
  USING (true);

CREATE POLICY task_log_write ON task_log
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL OR current_setting('app.api_key') IS NOT NULL);

-- Public policy for learning_cycles
CREATE POLICY learning_cycles_read ON learning_cycles
  FOR SELECT
  USING (true);

-- Public policy for performance_metrics
CREATE POLICY performance_metrics_read ON performance_metrics
  FOR SELECT
  USING (true);

-- Grant permissions
GRANT SELECT ON task_log TO anon;
GRANT SELECT ON learning_cycles TO anon;
GRANT SELECT ON performance_metrics TO anon;
GRANT SELECT ON dashboard_config TO anon;

-- Create a view for easy dashboard queries
CREATE OR REPLACE VIEW dashboard_summary AS
SELECT
  (SELECT COUNT(*) FROM task_log WHERE created_at > NOW() - INTERVAL '24 hours') as tasks_last_24h,
  (SELECT SUM(tokens_used) FROM task_log WHERE created_at > NOW() - INTERVAL '24 hours') as total_tokens_24h,
  (SELECT SUM(cost) FROM task_log WHERE created_at > NOW() - INTERVAL '24 hours') as total_cost_24h,
  (SELECT COUNT(*) FILTER (WHERE status = 'success') FROM task_log WHERE created_at > NOW() - INTERVAL '24 hours')::FLOAT / 
  NULLIF(COUNT(*), 0) * 100 as success_rate_24h,
  (SELECT AVG(duration_ms) FROM task_log WHERE created_at > NOW() - INTERVAL '24 hours') as avg_duration_ms;

GRANT SELECT ON dashboard_summary TO anon;

-- Migration: Set updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agent_memory_updated_at BEFORE UPDATE ON agent_memory
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_cycles_updated_at BEFORE UPDATE ON learning_cycles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dashboard_config_updated_at BEFORE UPDATE ON dashboard_config
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- All done!
-- Tables created: agent_memory, task_log, learning_cycles, performance_metrics, dashboard_config
-- Indexes created for fast queries on: session_id, model_used, status, created_at, cost
-- RLS enabled for public read access to metrics
-- Dashboard view created for quick summary queries
