-- 011_refactor_positions_to_securities.sql

-- Step 1: Create the new 'securities' table to store static instrument data.
-- This table will prevent data duplication for symbols that appear in multiple user accounts.
CREATE TABLE public.securities (
    id uuid NOT NULL,
    symbol text NOT NULL,
    description text,
    currency_code text,
    exchange_name text,
    figi_code text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT securities_pkey PRIMARY KEY (id)
);

COMMENT ON TABLE public.securities IS 'Stores static, universal information about financial securities (stocks, ETFs, etc.).';
COMMENT ON COLUMN public.securities.id IS 'The universal symbol ID from SnapTrade, used as the primary key.';
COMMENT ON COLUMN public.securities.symbol IS 'The ticker symbol (e.g., AAPL, VOO).';
COMMENT ON COLUMN public.securities.description IS 'The full name of the security.';
COMMENT ON COLUMN public.securities.currency_code IS 'The listing currency of the security.';
COMMENT ON COLUMN public.securities.exchange_name IS 'The name of the exchange where the security is listed.';
COMMENT ON COLUMN public.securities.figi_code IS 'The FIGI (Financial Instrument Global Identifier) code for the security.';

-- Associate the updated_at trigger with the new table
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON public.securities
FOR EACH ROW
EXECUTE PROCEDURE public.trigger_set_timestamp();

-- Enable RLS for the new securities table.
-- We can make this read-only for all authenticated users as it's not user-specific data.
ALTER TABLE public.securities ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow read access to all authenticated users"
ON public.securities
FOR SELECT
USING (auth.role() = 'authenticated');


-- Step 2: Add the foreign key column to the 'account_positions' table.
ALTER TABLE public.account_positions
ADD COLUMN security_id uuid;

-- Step 3: Add the foreign key constraint.
-- Note: In a live environment with data, a data migration step would be needed here
-- to populate 'securities' and 'security_id' before adding the constraint.
-- For this project, we assume a fresh sync will populate the data correctly.
ALTER TABLE public.account_positions
ADD CONSTRAINT account_positions_security_id_fkey
FOREIGN KEY (security_id) REFERENCES public.securities(id) ON DELETE SET NULL;

-- Step 4: Drop the old, redundant columns from 'account_positions'.
ALTER TABLE public.account_positions
DROP COLUMN symbol,
DROP COLUMN description;

-- Update comments for the modified table
COMMENT ON TABLE public.account_positions IS 'Stores user-specific position data, linked to a universal security.';
COMMENT ON COLUMN public.account_positions.security_id IS 'FK to securities.id, linking the position to a universal security.';
