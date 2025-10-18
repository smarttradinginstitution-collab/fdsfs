-- V4__add_starting_balance_to_notes.sql

-- Add the starting_balance_of_day column to the notes table.
-- This column will store the trading account balance at the moment the user
-- starts their day, to be used as a basis for percentage-based rules.
-- It is nullable because it only applies to notes that are "Daily Journals".
ALTER TABLE public.notes
ADD COLUMN starting_balance_of_day NUMERIC;