-- 010_add_details_to_accounts.sql

-- Add new columns to the brokerage_accounts table for enriched data
ALTER TABLE public.brokerage_accounts
ADD COLUMN status TEXT,
ADD COLUMN sync_status JSONB;

-- Add comments for the new columns
COMMENT ON COLUMN public.brokerage_accounts.status IS 'The status of the account (e.g., "open", "closed"), synced from SnapTrade.';
COMMENT ON COLUMN public.brokerage_accounts.sync_status IS 'The full sync status object from SnapTrade, providing details on data freshness.';
