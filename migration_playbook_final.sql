
-- ============================================================================
-- Final Playbook Feature Migration
--
-- This idempotent script consolidates all necessary database changes for the
-- new "Playbook Blocks" feature. It performs the following actions:
-- 1. Removes the obsolete "Conditions" feature tables.
-- 2. Safely drops and recreates the block type ENUM with the correct values.
-- 3. Alters the `playbook_blocks` table to use the new `block_type` ENUM.
-- ============================================================================

-- Step 1: Remove obsolete tables related to the old "Conditions" feature.
-- We drop the dependent table first to avoid foreign key constraint errors.
DROP TABLE IF EXISTS public.trade_condition_checks CASCADE;
DROP TABLE IF EXISTS public.playbook_conditions CASCADE;

-- Step 2: Safely rebuild the block type ENUM.
-- Drop any previous versions of the ENUM to ensure a clean state.
DROP TYPE IF EXISTS public.playbook_block_type CASCADE;
DROP TYPE IF EXISTS public.block_type_enum CASCADE;

-- Create the final, definitive ENUM with the three supported block types.
CREATE TYPE public.block_type_enum AS ENUM (
  'RULES',      -- For checklists, rules, and entry/exit criteria.
  'THESIS',     -- For rich text, analysis, and narrative content.
  'GALLERY'     -- For annotated screenshots and visual examples.
);

-- Step 3: Align the `playbook_blocks` table with the new ENUM.
-- First, drop the old column if it exists to avoid conflicts.
ALTER TABLE public.playbook_blocks DROP COLUMN IF EXISTS block_type;

-- Now, add the new column, linking it to the correct ENUM type and setting
-- a sensible default value.
ALTER TABLE public.playbook_blocks
ADD COLUMN block_type public.block_type_enum NOT NULL DEFAULT 'RULES';

-- Optional: Clean up old, unused blocks if necessary (currently disabled).
-- DELETE FROM public.playbook_blocks;

-- ============================================================================
-- Migration Complete
-- ============================================================================
