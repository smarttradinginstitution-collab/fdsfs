-- Create the option_symbols table to store centralized option data
CREATE TABLE IF NOT EXISTS public.option_symbols (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    option_type TEXT NOT NULL CHECK (option_type IN ('CALL', 'PUT')),
    strike_price NUMERIC NOT NULL,
    expiry_date DATE NOT NULL,
    underlying_symbol_id UUID NOT NULL REFERENCES public.securities(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add comments to the option_symbols table and its columns
COMMENT ON TABLE public.option_symbols IS 'Stores centralized data for option symbols, referenced by account activities.';
COMMENT ON COLUMN public.option_symbols.id IS 'The unique identifier for the option symbol from SnapTrade.';
COMMENT ON COLUMN public.option_symbols.description IS 'A human-readable description of the option.';
COMMENT ON COLUMN public.option_symbols.option_type IS 'The type of the option (CALL or PUT).';
COMMENT ON COLUMN public.option_symbols.strike_price IS 'The strike price of the option.';
COMMENT ON COLUMN public.option_symbols.expiry_date IS 'The expiration date of the option.';
COMMENT ON COLUMN public.option_symbols.underlying_symbol_id IS 'A foreign key to the underlying security in the securities table.';


-- Create the account_activities table to store transaction history
CREATE TABLE IF NOT EXISTS public.account_activities (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES public.brokerage_accounts(id) ON DELETE CASCADE,
    security_id UUID REFERENCES public.securities(id) ON DELETE CASCADE,
    option_symbol_id TEXT REFERENCES public.option_symbols(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    option_type TEXT,
    price NUMERIC,
    units NUMERIC,
    amount NUMERIC,
    description TEXT,
    trade_date TIMESTAMPTZ,
    settlement_date TIMESTAMPTZ,
    fee NUMERIC,
    fx_rate NUMERIC,
    institution TEXT,
    external_reference_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT check_security_or_option CHECK (
        (security_id IS NOT NULL AND option_symbol_id IS NULL) OR
        (security_id IS NULL AND option_symbol_id IS NOT NULL) OR
        (security_id IS NOT NULL AND option_symbol_id IS NOT NULL) OR
        (security_id IS NULL AND option_symbol_id IS NULL)
    )
);

-- Add comments to the account_activities table and its columns
COMMENT ON TABLE public.account_activities IS 'Stores historical account activities (transactions) synced from SnapTrade.';
COMMENT ON COLUMN public.account_activities.id IS 'The unique identifier for the activity from SnapTrade.';
COMMENT ON COLUMN public.account_activities.user_id IS 'A foreign key to the user who owns the account.';
COMMENT ON COLUMN public.account_activities.account_id IS 'A foreign key to the brokerage account this activity belongs to.';
COMMENT ON COLUMN public.account_activities.security_id IS 'A foreign key to the security involved in the activity (nullable).';
COMMENT ON COLUMN public.account_activities.option_symbol_id IS 'A foreign key to the option symbol involved in the activity (nullable).';
COMMENT ON COLUMN public.account_activities.type IS 'The type of activity (e.g., BUY, SELL, DIVIDEND).';
COMMENT ON COLUMN public.account_activities.option_type IS 'The type of option involved, if applicable (e.g., CALL, PUT).';
COMMENT ON COLUMN public.account_activities.price IS 'The price per unit of the security or option.';
COMMENT ON COLUMN public.account_activities.units IS 'The number of units transacted.';
COMMENT ON COLUMN public.account_activities.amount IS 'The total monetary value of the activity.';
COMMENT ON COLUMN public.account_activities.description IS 'A description of the activity provided by the institution.';
COMMENT ON COLUMN public.account_activities.trade_date IS 'The date the trade was executed.';
COMMENT ON COLUMN public.account_activities.settlement_date IS 'The date the trade settled.';
COMMENT ON COLUMN public.account_activities.fee IS 'Any fees associated with the activity.';
COMMENT ON COLUMN public.account_activities.fx_rate IS 'The foreign exchange rate applied, if any.';
COMMENT ON COLUMN public.account_activities.institution IS 'The institution reporting the activity.';
COMMENT ON COLUMN public.account_activities.external_reference_id IS 'An external reference ID for the activity.';

-- Create indexes for faster querying
CREATE INDEX IF NOT EXISTS idx_account_activities_account_id ON public.account_activities(account_id);
CREATE INDEX IF NOT EXISTS idx_account_activities_type ON public.account_activities(type);
CREATE INDEX IF NOT EXISTS idx_option_symbols_underlying_id ON public.option_symbols(underlying_symbol_id);
