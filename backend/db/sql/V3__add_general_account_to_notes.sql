-- V3__add_general_account_to_notes.sql

-- 1. Add the general_account_id column to the notes table
-- This column will link each note directly to a general account.
-- It is set to nullable initially to allow backfilling existing records.
ALTER TABLE public.notes
ADD COLUMN general_account_id UUID;

-- 2. Backfill the general_account_id for existing notes
-- This query updates all existing notes, setting their general_account_id
-- based on the general_account_id of their parent notebook_folder.
UPDATE public.notes n
SET general_account_id = f.general_account_id
FROM public.notebook_folders f
WHERE n.folder_id = f.id;

-- 3. Add a foreign key constraint to the new column
-- This enforces data integrity, ensuring every note is linked to a valid general account.
ALTER TABLE public.notes
ADD CONSTRAINT fk_notes_general_account
FOREIGN KEY (general_account_id)
REFERENCES public.general_accounts(id)
ON DELETE CASCADE;

-- 4. Set the column to NOT NULL
-- After backfilling, we can enforce that all new notes must have a general_account_id.
ALTER TABLE public.notes
ALTER COLUMN general_account_id SET NOT NULL;