-- This script is now idempotent and can be run multiple times safely.

-- Drop existing objects in reverse order of dependency to avoid errors.
DROP TABLE IF EXISTS public.trade_condition_checks CASCADE;
DROP TABLE IF EXISTS public.playbook_conditions CASCADE;
DROP TABLE IF EXISTS public.playbook_blocks CASCADE;
DROP TYPE IF EXISTS public.playbook_block_type CASCADE;

-- Create the ENUM type for playbook blocks
CREATE TYPE public.playbook_block_type AS ENUM (
  'THESIS',
  'GALLERY',
  'CONDITIONS',
  'PSYCHOLOGY',
  'LEGACY_RULES'
);

-- Create the playbook_blocks table
CREATE TABLE public.playbook_blocks (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  playbook_id uuid NOT NULL REFERENCES public.playbooks(id) ON DELETE CASCADE,
  block_type public.playbook_block_type NOT NULL,
  content jsonb,
  "order" integer,
  created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- Create the playbook_conditions table
CREATE TABLE public.playbook_conditions (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  playbook_id uuid NOT NULL REFERENCES public.playbooks(id) ON DELETE CASCADE,
  category text NOT NULL,
  variable text NOT NULL,
  operator text NOT NULL,
  "value" jsonb NOT NULL,
  "order" integer,
  created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- Create the trade_condition_checks table
CREATE TABLE public.trade_condition_checks (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  trade_id uuid NOT NULL REFERENCES public.trades(id) ON DELETE CASCADE,
  condition_id uuid NOT NULL REFERENCES public.playbook_conditions(id) ON DELETE CASCADE,
  was_met boolean NOT NULL,
  live_value text,
  created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- Safely add the playbook_id column to the images table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name='images' AND column_name='playbook_id') THEN
        ALTER TABLE public.images ADD COLUMN playbook_id uuid REFERENCES public.playbooks(id) ON DELETE SET NULL;
    END IF;
END $$;
