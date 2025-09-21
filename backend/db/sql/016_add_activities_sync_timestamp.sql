-- Add a new column to the brokerage_accounts table to track the last time
-- account activities were successfully synchronized.
ALTER TABLE public.brokerage_accounts
ADD COLUMN IF NOT EXISTS last_activities_synced_at TIMESTAMPTZ;

COMMENT ON COLUMN public.brokerage_accounts.last_activities_synced_at IS 'Timestamp of the last successful synchronization of account activities from SnapTrade.';
