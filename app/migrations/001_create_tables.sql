-- 001_create_tables.sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- users
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  full_name VARCHAR(255),
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- user_settings
CREATE TABLE IF NOT EXISTS user_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  telegram_token TEXT,
  telegram_chat_id TEXT,
  notify_pump BOOLEAN DEFAULT TRUE,
  notify_dump BOOLEAN DEFAULT TRUE,
  notify_reversal BOOLEAN DEFAULT TRUE,
  notify_stagnant BOOLEAN DEFAULT TRUE,
  notify_low_volume BOOLEAN DEFAULT TRUE,
  last_notification_at TIMESTAMP WITH TIME ZONE
);

-- admin_settings (single row expected)
CREATE TABLE IF NOT EXISTS admin_settings (
  id SERIAL PRIMARY KEY,
  global_notifications BOOLEAN DEFAULT TRUE,
  pump_detector_on BOOLEAN DEFAULT TRUE,
  dump_detector_on BOOLEAN DEFAULT TRUE,
  reversal_detector_on BOOLEAN DEFAULT TRUE,
  stagnant_detector_on BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- pump_history
CREATE TABLE IF NOT EXISTS pump_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  coin VARCHAR(64) NOT NULL,
  price NUMERIC,
  volume NUMERIC,
  percent_change NUMERIC,
  detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  exchange VARCHAR(64)
);

-- user_coin_history (linking table if needed)
CREATE TABLE IF NOT EXISTS user_coin_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  coin_history_id UUID NOT NULL REFERENCES pump_history(id) ON DELETE CASCADE
);

-- notifications log
CREATE TABLE IF NOT EXISTS logs_notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  symbol VARCHAR(64),
  type VARCHAR(32),
  payload JSONB,
  sent_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- trigger to update updated_at
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TRIGGER set_timestamp_admin_settings
BEFORE UPDATE ON admin_settings
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
