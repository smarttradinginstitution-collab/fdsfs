-- File: 004_import_schema_base.sql
-- Description: Creates the base schema for the trade import functionality.
-- This includes extensions, ENUM types, new tables (import_runs, asset_aliases),
-- and hardening of existing tables like platforms and broker relationships.

-- 1) Prerequisites & Extensions
-- Executed once at the database level
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS citext;    -- for case-insensitive text

-- 2) ENUM Types
DO $$
BEGIN
  -- This custom ENUM will replace the one defined in the ORM for consistency
  -- across all new import-related features.
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

-- 3) Table import_runs (for batch auditing)
CREATE TABLE IF NOT EXISTS public.import_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  trading_account_id uuid NOT NULL REFERENCES public.trading_accounts(id) ON DELETE CASCADE,
  platform_id uuid REFERENCES public.platforms(id) ON DELETE SET NULL, -- Platform can be nullable
  source_type public.import_source_type NOT NULL,
  file_name text,
  file_sha256 text,
  status text NOT NULL DEFAULT 'queued', -- queued | parsing | applied | failed
  total_rows int DEFAULT 0,
  inserted_count int DEFAULT 0,
  updated_count int DEFAULT 0,
  skipped_count int DEFAULT 0,
  error_message text,
  created_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_import_runs_user_acc_created
  ON public.import_runs (user_id, trading_account_id, created_at DESC);

-- 4) Hardening platforms table
-- Note: The 'platforms' table does not exist yet and needs to be created.
-- The original plan assumed it existed. We create it here.
CREATE TABLE IF NOT EXISTS public.platforms (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name citext NOT NULL UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT platforms_name_not_blank_chk CHECK (btrim(name) <> '')
);

-- Generic function to update the 'updated_at' timestamp
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at := now(); RETURN NEW; END $$;

-- Trigger for platforms updated_at
DROP TRIGGER IF EXISTS trg_platforms_set_updated_at ON public.platforms;
CREATE TRIGGER trg_platforms_set_updated_at
BEFORE UPDATE ON public.platforms
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 5) Broker/Account/Platform Relationships
-- Create broker_platforms join table
CREATE TABLE IF NOT EXISTS public.broker_platforms (
    broker_id uuid NOT NULL REFERENCES public.brokers(id) ON DELETE CASCADE,
    platform_id uuid NOT NULL REFERENCES public.platforms(id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (broker_id, platform_id)
);

CREATE INDEX IF NOT EXISTS idx_broker_platforms_broker ON public.broker_platforms (broker_id);
CREATE INDEX IF NOT EXISTS idx_broker_platforms_platform ON public.broker_platforms (platform_id);

-- Enforce: 1 trading account -> 1 broker
ALTER TABLE public.trading_accounts
  ALTER COLUMN broker_id SET NOT NULL;

-- 8) Uniqueness for user-specific resources
ALTER TABLE public.tags
  ADD CONSTRAINT IF NOT EXISTS uq_tags_name_per_account UNIQUE (general_account_id, name);

ALTER TABLE public.mistakes
  ADD CONSTRAINT IF NOT EXISTS uq_mistakes_name_per_account UNIQUE (general_account_id, name);

ALTER TABLE public.playbooks
  ADD CONSTRAINT IF NOT EXISTS uq_playbooks_title_per_account UNIQUE (general_account_id, title);

-- Note: Assuming news_impacts and psychology_states exist and have general_account_id
-- If not, these statements will need adjustment.
-- ALTER TABLE public.news_impacts
--   ADD CONSTRAINT IF NOT EXISTS uq_news_impacts_title_per_account UNIQUE (general_account_id, title);
--
-- ALTER TABLE public.psychology_states
--   ADD CONSTRAINT IF NOT EXISTS uq_psychology_state_per_account UNIQUE (general_account_id, state);

-- 9) (Optional but useful) asset_aliases table
CREATE TABLE IF NOT EXISTS public.asset_aliases (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id uuid NOT NULL REFERENCES public.assets(id) ON DELETE CASCADE,
  -- broker_id can be useful for broker-specific aliases
  broker_id uuid REFERENCES public.brokers(id) ON DELETE CASCADE,
  -- platform_id is crucial for platform-specific aliases like in Tradovate
  platform_id uuid REFERENCES public.platforms(id) ON DELETE CASCADE,
  alias text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  -- An alias should be unique for a given platform/broker to avoid ambiguity
  UNIQUE (platform_id, broker_id, alias)
);

CREATE INDEX IF NOT EXISTS idx_asset_alias_alias ON public.asset_aliases (alias);