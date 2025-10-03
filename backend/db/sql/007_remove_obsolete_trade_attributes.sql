-- Drop specified columns from the public.trades table
ALTER TABLE public.trades
DROP COLUMN IF EXISTS setup,
DROP COLUMN IF EXISTS notes,
DROP COLUMN IF EXISTS symbol,
DROP COLUMN IF EXISTS emotional_state,
DROP COLUMN IF EXISTS notes_pre_trade,
DROP COLUMN IF EXISTS notes_post_trade,
DROP COLUMN IF EXISTS asset_name_snapshot;