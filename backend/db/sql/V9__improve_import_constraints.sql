-- File: V9__improve_import_constraints.sql
-- Description: Changes uniqueness constraints for import_runs and trades to be scoped by trading_account.

-- 1. Import Runs: Change uniqueness of file_sha256 from global to per-account.
-- We first attempt to drop the likely constraint name. If it differs, manual intervention might be needed,
-- but standard naming is table_column_key.
ALTER TABLE public.import_runs
    DROP CONSTRAINT IF EXISTS import_runs_file_sha256_key;

-- Create the new composite unique index.
CREATE UNIQUE INDEX IF NOT EXISTS uq_import_runs_hash_account
    ON public.import_runs (file_sha256, trading_account_id);


-- 2. Trades: Add composite unique constraint on (trading_account_id, dedupe_key).
-- We filter where dedupe_key is NOT NULL to allow nulls (though ideally it shouldn't be null).
CREATE UNIQUE INDEX IF NOT EXISTS uq_trades_account_dedupe
    ON public.trades (trading_account_id, dedupe_key)
    WHERE dedupe_key IS NOT NULL;
