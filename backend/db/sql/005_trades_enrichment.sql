-- File: 005_trades_enrichment.sql
-- Description: Enriches the 'trades' table with new columns and indexes
-- required for the import functionality and data deduplication.

-- 6) Trades Enrichment
-- Add new columns idempotently
ALTER TABLE public.trades
  ADD COLUMN IF NOT EXISTS status public.trade_status DEFAULT 'closed',
  ADD COLUMN IF NOT EXISTS platform_id uuid REFERENCES public.platforms(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS import_run_id uuid REFERENCES public.import_runs(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS external_id text,
  ADD COLUMN IF NOT EXISTS dedupe_key text,
  ADD COLUMN IF NOT EXISTS symbol_snapshot text,
  ADD COLUMN IF NOT EXISTS asset_name_snapshot text,
  ADD COLUMN IF NOT EXISTS fees numeric(19, 4) DEFAULT 0,
  ADD COLUMN IF NOT EXISTS commissions numeric(19, 4) DEFAULT 0,
  ADD COLUMN IF NOT EXISTS currency char(3),
  ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

-- Replace the old 'direction' column (which was a different ENUM) with the new one.
-- First, drop the existing direction column if it exists. The ORM model used a different ENUM definition.
-- The new column 'direction' will be added later from 'direction_enum_temp'.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema='public' AND table_name='trades' AND column_name='direction') THEN
    ALTER TABLE public.trades DROP COLUMN direction;
  END IF;
END$$;

-- Add the new direction column with the correct public.trade_direction ENUM type.
ALTER TABLE public.trades
  ADD COLUMN IF NOT EXISTS direction public.trade_direction;


-- Deduplication and idempotency indexes
-- This index ensures that a trade with a specific external ID from a platform is unique for a given trading account.
CREATE UNIQUE INDEX IF NOT EXISTS uq_trades_ext_per_acc_platform
  ON public.trades (trading_account_id, platform_id, external_id)
  WHERE external_id IS NOT NULL;

-- This index is a fallback for sources that do not provide a clean external_id.
-- The import logic will construct a unique hash (e.g., from timestamps, prices, symbol).
CREATE UNIQUE INDEX IF NOT EXISTS uq_trades_dedupe_per_acc
  ON public.trades (trading_account_id, dedupe_key)
  WHERE dedupe_key IS NOT NULL;


-- Operational indexes for performance
CREATE INDEX IF NOT EXISTS idx_trades_account_created
  ON public.trades (trading_account_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_trades_asset
  ON public.trades (asset_id);


-- updated_at trigger for trades table
-- We reuse the generic function created in the previous script.
DROP TRIGGER IF EXISTS trg_trades_set_updated_at ON public.trades;
CREATE TRIGGER trg_trades_set_updated_at
BEFORE UPDATE ON public.trades
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


-- 7) Ambiguity cleanup on trades
-- Remove the 'mistakes' array column if it exists. The new schema uses a proper many-to-many join table.
-- From the model analysis, this is already handled, but we keep it for robustness.
ALTER TABLE public.trades DROP COLUMN IF EXISTS mistakes;

-- The 'emotional_state' column was optional and not found in the current ORM model.
-- This line is commented out to avoid errors if the column truly doesn't exist.
-- ALTER TABLE public.trades DROP COLUMN IF EXISTS emotional_state;