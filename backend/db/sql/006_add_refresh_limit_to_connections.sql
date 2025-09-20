ALTER TABLE public.brokerage_connections
ADD COLUMN manual_refresh_count INTEGER NOT NULL DEFAULT 0,
ADD COLUMN last_manual_refresh_at TIMESTAMPTZ;
