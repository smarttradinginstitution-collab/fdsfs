-- This migration re-introduces the block_type column to support polymorphic blocks.
ALTER TABLE public.playbook_blocks ADD COLUMN IF NOT EXISTS block_type TEXT NOT NULL DEFAULT 'RULES';
