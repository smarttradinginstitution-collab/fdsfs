-- This script updates the 'import_source_type' enum to include new values for MT5 and Tradovate imports.
-- It should be run to prevent "invalid input value for enum" errors.
-- The values are added with IF NOT EXISTS to be safe to run multiple times.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'tradovate_csv' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'import_source_type')) THEN
        ALTER TYPE public.import_source_type ADD VALUE 'tradovate_csv';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'mt5_html' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'import_source_type')) THEN
        ALTER TYPE public.import_source_type ADD VALUE 'mt5_html';
    END IF;
END$$;