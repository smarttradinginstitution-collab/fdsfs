-- This migration script removes the now-obsolete "Conditions" feature.

-- Drop the dependent table first to avoid foreign key constraint errors.
DROP TABLE IF EXISTS public.trade_condition_checks;

-- Drop the main conditions table.
DROP TABLE IF EXISTS public.playbook_conditions;
