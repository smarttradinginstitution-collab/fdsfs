-- This script should be run AFTER the new playbook schema is created and the
-- data has been successfully migrated by the `migrate_legacy_rules.py` script.
-- It removes the old, now redundant, playbook-related tables.

-- Drop the many-to-many table linking trades to the old rules first
-- to avoid foreign key constraint issues.
DROP TABLE IF EXISTS public.trades_rules;

-- Drop the table containing the individual rule text.
DROP TABLE IF EXISTS public.rules_playbook;

-- Finally, drop the table that grouped the rules.
DROP TABLE IF EXISTS public.rules_groups_playbook;

-- Note: The order of dropping is important to respect foreign key constraints.
-- `trades_rules` depends on `rules_playbook`.
-- `rules_playbook` depends on `rules_groups_playbook`.
