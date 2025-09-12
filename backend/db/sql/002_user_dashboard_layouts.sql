-- Migration for user_dashboard_layouts table
CREATE TABLE user_dashboard_layouts (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    layout JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Optional: Add a trigger to automatically update updated_at on row modification.
-- This is good practice if updates happen directly in the DB.
-- For now, we'll rely on the application layer (SQLAlchemy's onupdate) to handle this.
--
-- CREATE OR REPLACE FUNCTION trigger_set_timestamp()
-- RETURNS TRIGGER AS $$
-- BEGIN
--   NEW.updated_at = NOW();
--   RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;
--
-- CREATE TRIGGER set_timestamp
-- BEFORE UPDATE ON user_dashboard_layouts
-- FOR EACH ROW
-- EXECUTE PROCEDURE trigger_set_timestamp();
