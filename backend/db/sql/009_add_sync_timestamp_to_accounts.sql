-- Add last_synced_at to brokerage_accounts to track holdings sync
ALTER TABLE public.brokerage_accounts
ADD COLUMN last_synced_at TIMESTAMPTZ;
