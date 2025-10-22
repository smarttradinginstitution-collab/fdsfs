-- Add is_reviewed column to trades table
ALTER TABLE public.trades
ADD COLUMN is_reviewed BOOLEAN NOT NULL DEFAULT false;
