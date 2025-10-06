-- This script updates the database schema to support typed system folders for the notebook feature.

-- 1. Create the new ENUM type for identifying specific system folders.
-- This allows the frontend to have robust logic based on a type rather than a folder name.
CREATE TYPE public.system_folder_identifier AS ENUM (
    'NONE',
    'TRADE_NOTES',
    'DAILY_JOURNAL',
    'SESSION_RECAP'
);

-- 2. Add the new 'system_folder_identifier' column to the 'notebook_folders' table.
-- This column will store the specific type of system folder.
-- It defaults to 'NONE' for all existing and new user-created folders.
ALTER TABLE public.notebook_folders
ADD COLUMN system_folder_identifier public.system_folder_identifier NOT NULL DEFAULT 'NONE';

-- Note: The 'deleted_at' and 'is_system_folder' columns were already present
-- in the schema you provided, so they are not included in this migration script.
-- My previous model updates were to align the application code with your schema.