-- This script updates the database schema and populates it with initial data.

-- Step 1: Add 'initial_balance' and 'currency' columns to the 'trading_accounts' table.
-- The 'currency' column includes a CHECK constraint to allow only specific values.
ALTER TABLE public.trading_accounts
ADD COLUMN initial_balance NUMERIC,
ADD COLUMN currency TEXT CHECK (currency IN ('EUR', 'USD', 'GBP'));

-- Step 2: Create the 'Tradovate' broker if it doesn't already exist.
INSERT INTO public.brokers (name)
VALUES ('Tradovate')
ON CONFLICT (name) DO NOTHING;

-- Step 3: Create the 'Tradovate' platform if it doesn't already exist.
-- Assuming the 'name' column in the 'platforms' table is of a USER-DEFINED type that can be cast from a string.
INSERT INTO public.platforms (name)
VALUES ('Tradovate')
ON CONFLICT (name) DO NOTHING;

-- Step 4: Link the 'Tradovate' broker to the 'Tradovate' platform.
-- This ensures that 'Tradovate' is a valid broker/platform combination.
DO $$
DECLARE
    tradovate_broker_id UUID;
    tradovate_platform_id UUID;
BEGIN
    -- Get the IDs for the 'Tradovate' broker and platform.
    SELECT id INTO tradovate_broker_id FROM public.brokers WHERE name = 'Tradovate';
    SELECT id INTO tradovate_platform_id FROM public.platforms WHERE name = 'Tradovate';

    -- Insert the link only if it doesn't already exist.
    IF tradovate_broker_id IS NOT NULL AND tradovate_platform_id IS NOT NULL THEN
        INSERT INTO public.broker_platforms (broker_id, platform_id)
        SELECT tradovate_broker_id, tradovate_platform_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM public.broker_platforms
            WHERE broker_id = tradovate_broker_id AND platform_id = tradovate_platform_id
        );
    END IF;
END $$;

-- Step 5: Link the 'DEMO' broker to all available platforms.
-- This is useful for testing and demonstration purposes.
DO $$
DECLARE
    demo_broker_id UUID;
BEGIN
    -- Get the ID for the 'DEMO' broker.
    SELECT id INTO demo_broker_id FROM public.brokers WHERE name = 'DEMO';

    -- If the 'DEMO' broker exists, link it to all platforms it isn't already linked to.
    IF demo_broker_id IS NOT NULL THEN
        INSERT INTO public.broker_platforms (broker_id, platform_id)
        SELECT demo_broker_id, p.id
        FROM public.platforms p
        WHERE NOT EXISTS (
            SELECT 1
            FROM public.broker_platforms bp
            WHERE bp.broker_id = demo_broker_id AND bp.platform_id = p.id
        );
    END IF;
END $$;

-- Step 6: Add new values to the 'import_source_type' enum.
-- This ensures the database accepts the new source types from the application.
-- The 'IF NOT EXISTS' clause prevents errors if the script is run more than once.
ALTER TYPE public.import_source_type ADD VALUE IF NOT EXISTS 'TRADOVATE_CSV';
ALTER TYPE public.import_source_type ADD VALUE IF NOT EXISTS 'MT5_HTML';

-- End of script.