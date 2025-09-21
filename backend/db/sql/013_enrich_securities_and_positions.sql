-- Migration script to enrich the securities and account_positions tables
-- with all available fields from the SnapTrade /positions endpoint.

-- Step 1: Add new columns to the 'securities' table for universal symbol details.
ALTER TABLE public.securities
ADD COLUMN raw_symbol TEXT,
ADD COLUMN mic_code TEXT,
ADD COLUMN timezone TEXT,
ADD COLUMN start_time TEXT,
ADD COLUMN close_time TEXT,
ADD COLUMN suffix TEXT,
ADD COLUMN type_code TEXT,
ADD COLUMN type_description TEXT,
ADD COLUMN figi_share_class TEXT;

COMMENT ON COLUMN public.securities.raw_symbol IS 'The raw symbol without any exchange suffixes.';
COMMENT ON COLUMN public.securities.mic_code IS 'The Market Identifier Code (MIC) for the exchange.';
COMMENT ON COLUMN public.securities.timezone IS 'The timezone of the exchange (e.g., America/New_York).';
COMMENT ON COLUMN public.securities.start_time IS 'The opening time of the exchange.';
COMMENT ON COLUMN public.securities.close_time IS 'The closing time of the exchange.';
COMMENT ON COLUMN public.securities.suffix IS 'The exchange-specific suffix for the symbol (e.g., .TO).';
COMMENT ON COLUMN public.securities.type_code IS 'A short code for the security type (e.g., cs, etf).';
COMMENT ON COLUMN public.securities.type_description IS 'A human-readable description of the security type (e.g., Common Stock).';
COMMENT ON COLUMN public.securities.figi_share_class IS 'FIGI Share Class Identifier for linking securities across exchanges.';

-- Step 2: Add new column to the 'account_positions' table for position-specific details.
ALTER TABLE public.account_positions
ADD COLUMN cash_equivalent BOOLEAN;

COMMENT ON COLUMN public.account_positions.cash_equivalent IS 'Indicates if the position is a cash equivalent (e.g., money market fund).';
