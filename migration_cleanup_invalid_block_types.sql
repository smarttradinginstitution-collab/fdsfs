-- This script cleans up legacy data by updating old 'RULES' block types to the new 'CONDITIONS' type.
UPDATE public.playbook_blocks
SET block_type = 'CONDITIONS'
WHERE block_type = 'RULES';
