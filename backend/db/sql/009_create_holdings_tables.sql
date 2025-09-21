-- 009_create_holdings_tables.sql

-- Create account_positions table
CREATE TABLE public.account_positions (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    account_id uuid NOT NULL,
    symbol text NOT NULL,
    description text,
    units numeric NOT NULL,
    price numeric,
    currency text,
    open_pnl numeric,
    average_purchase_price numeric,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT account_positions_pkey PRIMARY KEY (id),
    CONSTRAINT account_positions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.brokerage_accounts(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.account_positions IS 'Stores detailed information about the positions (stocks, ETFs, crypto) in a trading account.';
COMMENT ON COLUMN public.account_positions.account_id IS 'FK to brokerage_accounts.id, linking the position to a specific account.';

-- Create account_balances table
CREATE TABLE public.account_balances (
    account_id uuid NOT NULL,
    currency_code text NOT NULL,
    cash_amount numeric,
    buying_power numeric,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT account_balances_pkey PRIMARY KEY (account_id, currency_code),
    CONSTRAINT account_balances_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.brokerage_accounts(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.account_balances IS 'Stores cash and buying power balances for a trading account, per currency.';
COMMENT ON COLUMN public.account_balances.account_id IS 'FK to brokerage_accounts.id, linking the balance to a specific account.';
COMMENT ON COLUMN public.account_balances.currency_code IS 'The currency code (e.g., USD, CAD). Part of the composite PK.';

-- Create account_orders table
CREATE TABLE public.account_orders (
    id text NOT NULL,
    account_id uuid NOT NULL,
    symbol text NOT NULL,
    action text,
    status text,
    total_quantity numeric,
    filled_quantity numeric,
    execution_price numeric,
    limit_price numeric,
    time_placed timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT account_orders_pkey PRIMARY KEY (id),
    CONSTRAINT account_orders_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.brokerage_accounts(id) ON DELETE CASCADE
);

COMMENT ON TABLE public.account_orders IS 'Stores trading orders placed within an account.';
COMMENT ON COLUMN public.account_orders.id IS 'The brokerage_order_id from SnapTrade, used as the primary key.';
COMMENT ON COLUMN public.account_orders.account_id IS 'FK to brokerage_accounts.id, linking the order to a specific account.';

-- Helper function to get user_id from account_id
CREATE OR REPLACE FUNCTION get_user_id_from_account(acc_id uuid)
RETURNS uuid AS $$
DECLARE
    user_id uuid;
BEGIN
    SELECT ba.user_id INTO user_id
    FROM public.brokerage_accounts ba
    WHERE ba.id = acc_id;
    RETURN user_id;
END;
$$ LANGUAGE plpgsql;

-- Enable RLS and define policies for account_positions
ALTER TABLE public.account_positions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow users to manage their own account positions"
ON public.account_positions
FOR ALL
USING (auth.uid() = get_user_id_from_account(account_id))
WITH CHECK (auth.uid() = get_user_id_from_account(account_id));

-- Enable RLS and define policies for account_balances
ALTER TABLE public.account_balances ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow users to manage their own account balances"
ON public.account_balances
FOR ALL
USING (auth.uid() = get_user_id_from_account(account_id))
WITH CHECK (auth.uid() = get_user_id_from_account(account_id));

-- Enable RLS and define policies for account_orders
ALTER TABLE public.account_orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow users to manage their own account orders"
ON public.account_orders
FOR ALL
USING (auth.uid() = get_user_id_from_account(account_id))
WITH CHECK (auth.uid() = get_user_id_from_account(account_id));

-- Triggers to update 'updated_at' on row update for the new tables
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON public.account_positions
FOR EACH ROW
EXECUTE PROCEDURE public.trigger_set_timestamp();

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON public.account_balances
FOR EACH ROW
EXECUTE PROCEDURE public.trigger_set_timestamp();

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON public.account_orders
FOR EACH ROW
EXECUTE PROCEDURE public.trigger_set_timestamp();
