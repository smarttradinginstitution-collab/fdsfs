-- This script completes the migration to the new playbook block system.

-- Step 1: Add the missing 'title' column to the playbook_blocks table
ALTER TABLE public.playbook_blocks ADD COLUMN title TEXT NOT NULL DEFAULT 'New Block';

-- Step 2: Drop the obsolete columns from the playbook_blocks table
ALTER TABLE public.playbook_blocks DROP COLUMN block_type;
ALTER TABLE public.playbook_blocks DROP COLUMN "order";

-- Step 3: Drop the dependent trade_condition_checks table, which is now obsolete
DROP TABLE public.trade_condition_checks;

-- Step 4: Drop the main playbook_conditions table, which is also obsolete
DROP TABLE public.playbook_conditions;
