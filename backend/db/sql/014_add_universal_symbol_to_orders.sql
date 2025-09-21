-- Migration script to add the universal_symbol field to the account_orders table.
-- This is necessary to store the full security object provided by the SnapTrade API,
-- ensuring we capture all available data as per our strategic goal.

ALTER TABLE public.account_orders
ADD COLUMN universal_symbol JSONB;

COMMENT ON COLUMN public.account_orders.universal_symbol IS 'Stores the full universal symbol object from SnapTrade, containing detailed security information.';
