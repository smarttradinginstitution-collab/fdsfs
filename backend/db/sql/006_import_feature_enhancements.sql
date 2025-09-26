-- SQL Migration file: 006_import_feature_enhancements.sql
-- This script implements the database changes required for the new import feature.
-- It is designed to be idempotent.

-- 1) Prerequisites & Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

-- 2) Standard ENUM Types
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trade_direction') THEN
    CREATE TYPE public.trade_direction AS ENUM ('long','short');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trade_status') THEN
    CREATE TYPE public.trade_status AS ENUM ('open','closed','cancelled');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'import_source_type') THEN
    CREATE TYPE public.import_source_type AS ENUM ('csv','html','xml','api','manual');
  END IF;
END$$;

-- 3) Table import_runs Enhancements
-- The table exists. We will align its 'source_type' with the new ENUM.
-- We will add a temporary column, backfill, drop the old one, and rename the new one.
ALTER TABLE public.import_runs ADD COLUMN IF NOT EXISTS source_type_new public.import_source_type;

-- For existing records, we'll assume 'manual' as a safe default.
UPDATE public.import_runs
SET source_type_new = 'manual'
WHERE source_type IS NOT NULL AND source_type_new IS NULL;

-- Now, perform the column swap
ALTER TABLE public.import_runs DROP COLUMN IF EXISTS source_type;
ALTER TABLE public.import_runs RENAME COLUMN source_type_new TO source_type;
ALTER TABLE public.import_runs ALTER COLUMN source_type SET NOT NULL;

-- Add index from the plan
CREATE INDEX IF NOT EXISTS idx_import_runs_acc_created
  ON public.import_runs (trading_account_id, created_at DESC);

-- 4) Hardening 'platforms' table
ALTER TABLE public.platforms
  ALTER COLUMN name TYPE public.citext,
  ALTER COLUMN name SET NOT NULL,
  ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now(),
  ADD CONSTRAINT IF NOT EXISTS platforms_name_not_blank_chk
  CHECK (btrim(name::text) <> '');

-- Generic function to set updated_at timestamp
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at := now(); RETURN NEW; END $$;

-- Trigger for 'platforms'
DROP TRIGGER IF EXISTS trg_platforms_set_updated_at ON public.platforms;
CREATE TRIGGER trg_platforms_set_updated_at
BEFORE UPDATE ON public.platforms
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 5) Relationships for broker/account/platform
ALTER TABLE public.trading_accounts
  ALTER COLUMN broker_id SET NOT NULL;

ALTER TABLE public.broker_platforms
  ADD CONSTRAINT IF NOT EXISTS uq_broker_platform UNIQUE (broker_id, platform_id);

CREATE INDEX IF NOT EXISTS idx_broker_platforms_broker ON public.broker_platforms (broker_id);
CREATE INDEX IF NOT EXISTS idx_broker_platforms_platform ON public.broker_platforms (platform_id);

ALTER TABLE public.broker_platforms
  DROP CONSTRAINT IF EXISTS broker_platforms_platform_id_fkey,
  ADD CONSTRAINT broker_platforms_platform_id_fkey
    FOREIGN KEY (platform_id) REFERENCES public.platforms(id) ON DELETE RESTRICT;

-- 6) Enrichments for 'trades' table
-- Migrate 'direction' from USER-DEFINED to the new ENUM
ALTER TABLE public.trades ADD COLUMN IF NOT EXISTS direction_new public.trade_direction;
UPDATE public.trades
SET direction_new = lower(direction::text)::public.trade_direction
WHERE direction IS NOT NULL AND direction_new IS NULL;
ALTER TABLE public.trades DROP COLUMN IF EXISTS direction;
ALTER TABLE public.trades RENAME COLUMN direction_new TO direction;

-- Migrate 'status' from USER-DEFINED to the new ENUM
ALTER TABLE public.trades ADD COLUMN IF NOT EXISTS status_new public.trade_status;
UPDATE public.trades
SET status_new = lower(status::text)::public.trade_status
WHERE status IS NOT NULL AND status_new IS NULL;
ALTER TABLE public.trades DROP COLUMN IF EXISTS status;
ALTER TABLE public.trades RENAME COLUMN status_new TO status;
ALTER TABLE public.trades ALTER COLUMN status SET DEFAULT 'closed';

-- Add other columns from the plan that might be missing
ALTER TABLE public.trades
  ADD COLUMN IF NOT EXISTS currency char(3);

-- Add updated_at trigger for 'trades'
DROP TRIGGER IF EXISTS trg_trades_set_updated_at ON public.trades;
CREATE TRIGGER trg_trades_set_updated_at
BEFORE UPDATE ON public.trades
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Add deduplication and operational indexes
CREATE UNIQUE INDEX IF NOT EXISTS uq_trades_ext_per_acc_platform
  ON public.trades (trading_account_id, platform_id, external_id)
  WHERE external_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_trades_dedupe_per_acc
  ON public.trades (trading_account_id, dedupe_key)
  WHERE dedupe_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_trades_account_created
  ON public.trades (trading_account_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_trades_asset
  ON public.trades (asset_id);

-- 7) Clean up ambiguous columns on 'trades'
ALTER TABLE public.trades DROP COLUMN IF EXISTS emotional_state;

-- 8) Add uniqueness constraints for user-specific resources
ALTER TABLE public.tags
  ADD CONSTRAINT IF NOT EXISTS uq_tags_name_per_account UNIQUE (general_account_id, name);

ALTER TABLE public.mistakes
  ADD CONSTRAINT IF NOT EXISTS uq_mistakes_name_per_account UNIQUE (general_account_id, name);

ALTER TABLE public.playbooks
  ADD CONSTRAINT IF NOT EXISTS uq_playbooks_title_per_account UNIQUE (general_account_id, title);

ALTER TABLE public.news_impacts
  ADD CONSTRAINT IF NOT EXISTS uq_news_impacts_title_per_account UNIQUE (general_account_id, title);

ALTER TABLE public.psychology_states
  ADD CONSTRAINT IF NOT EXISTS uq_psychology_state_per_account UNIQUE (general_account_id, state);

-- 9) Harden 'asset_aliases' table
ALTER TABLE public.asset_aliases
  ADD CONSTRAINT IF NOT EXISTS uq_asset_aliases_key UNIQUE (asset_id, broker_id, platform_id, alias);

-- 10) Data Backfill
-- Backfill trade status for any trades that might not have one after migration.
UPDATE public.trades
SET status = CASE
  WHEN exit_timestamp IS NULL THEN 'open'::public.trade_status
  ELSE 'closed'::public.trade_status
END
WHERE status IS NULL;