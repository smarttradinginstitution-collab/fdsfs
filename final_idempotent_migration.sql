-- This is the final, idempotent script to align the playbook schema.
-- It can be run multiple times without causing errors.

-- Step 1: Add the 'title' column to 'playbook_blocks' only if it doesn't already exist.
ALTER TABLE public.playbook_blocks ADD COLUMN IF NOT EXISTS title TEXT NOT NULL DEFAULT 'New Block';

-- Step 2: Drop the 'block_type' column from 'playbook_blocks' only if it exists.
ALTER TABLE public.playbook_blocks DROP COLUMN IF EXISTS block_type;

-- Step 3: Drop the 'order' column from 'playbook_blocks' only if it exists.
ALTER TABLE public.playbook_blocks DROP COLUMN IF EXISTS "order";

-- Step 4: Drop the 'trade_condition_checks' table only if it exists.
-- This table depends on 'playbook_conditions', so it must be dropped first.
DROP TABLE IF EXISTS public.trade_condition_checks;

-- Step 5: Drop the 'playbook_conditions' table only if it exists.
DROP TABLE IF EXISTS public.playbook_conditions;
