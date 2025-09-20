-- Migration script to create tables for account holdings, balances, and orders.

-- Table for account balances (cash, buying power)
CREATE TABLE public.account_balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    currency_code TEXT NOT NULL,
    cash_amount NUMERIC,
    buying_power NUMERIC,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_account
        FOREIGN KEY(account_id)
        REFERENCES public.brokerage_accounts(id)
        ON DELETE CASCADE
);
-- Add a unique constraint for upsert logic
ALTER TABLE public.account_balances ADD CONSTRAINT unique_account_currency UNIQUE (account_id, currency_code);

-- Table for account positions (stocks, ETFs, etc.)
CREATE TABLE public.account_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    description TEXT,
    units NUMERIC,
    price NUMERIC,
    currency TEXT,
    open_pnl NUMERIC,
    average_purchase_price NUMERIC,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_account
        FOREIGN KEY(account_id)
        REFERENCES public.brokerage_accounts(id)
        ON DELETE CASCADE
);
-- Add a unique constraint for upsert logic
ALTER TABLE public.account_positions ADD CONSTRAINT unique_account_symbol UNIQUE (account_id, symbol);

-- Table for account orders
CREATE TABLE public.account_orders (
    id TEXT PRIMARY KEY, -- Using brokerage_order_id from SnapTrade as PK
    account_id UUID NOT NULL,
    symbol TEXT,
    action TEXT,
    status TEXT,
    total_quantity NUMERIC,
    filled_quantity NUMERIC,
    execution_price NUMERIC,
    limit_price NUMERIC,
    time_placed TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_account
        FOREIGN KEY(account_id)
        REFERENCES public.brokerage_accounts(id)
        ON DELETE CASCADE
);

-- Add comments on tables and columns for clarity
COMMENT ON TABLE public.account_balances IS 'Stores cash and buying power for each currency in a brokerage account.';
COMMENT ON TABLE public.account_positions IS 'Stores asset positions (stocks, ETFs, etc.) for a brokerage account.';
COMMENT ON TABLE public.account_orders IS 'Stores trading orders for a brokerage account.';
COMMENT ON COLUMN public.account_orders.id IS 'The brokerage_order_id from SnapTrade, used as the primary key.';
