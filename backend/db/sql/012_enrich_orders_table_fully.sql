-- Migration script to fully enrich the account_orders table with all available fields
-- from the SnapTrade /orders endpoint and create a dedicated table for option details.

-- Step 1: Add all new scalar and simple object columns to the existing account_orders table.
ALTER TABLE public.account_orders
ADD COLUMN open_quantity NUMERIC,
ADD COLUMN canceled_quantity NUMERIC,
ADD COLUMN stop_price NUMERIC,
ADD COLUMN order_type TEXT,
ADD COLUMN time_in_force TEXT,
ADD COLUMN time_updated TIMESTAMPTZ,
ADD COLUMN time_executed TIMESTAMPTZ,
ADD COLUMN expiry_date TIMESTAMPTZ,
ADD COLUMN take_profit_order_id TEXT,
ADD COLUMN stop_loss_order_id TEXT,
ADD COLUMN quote_universal_symbol JSONB,
ADD COLUMN quote_currency JSONB;

COMMENT ON COLUMN public.account_orders.open_quantity IS 'Number of shares or contracts that are still open (waiting for execution).';
COMMENT ON COLUMN public.account_orders.canceled_quantity IS 'Number of shares or contracts that have been canceled.';
COMMENT ON COLUMN public.account_orders.stop_price IS 'The stop price is the price at which a stop order is triggered.';
COMMENT ON COLUMN public.account_orders.order_type IS 'The type of order placed (e.g., Market, Limit).';
COMMENT ON COLUMN public.account_orders.time_in_force IS 'The Time in Force type for the order (e.g., Day, GTC).';
COMMENT ON COLUMN public.account_orders.time_updated IS 'The time the order was last updated in the brokerage system.';
COMMENT ON COLUMN public.account_orders.time_executed IS 'The time the order was executed in the brokerage system.';
COMMENT ON COLUMN public.account_orders.expiry_date IS 'The time the order expires.';
COMMENT ON COLUMN public.account_orders.take_profit_order_id IS 'The brokerage order ID for the take profit leg of a bracket order.';
COMMENT ON COLUMN public.account_orders.stop_loss_order_id IS 'The brokerage order ID for the stop loss leg of a bracket order.';
COMMENT ON COLUMN public.account_orders.quote_universal_symbol IS 'Stores the quote cryptocurrency for crypto pair orders.';
COMMENT ON COLUMN public.account_orders.quote_currency IS 'Stores the quote fiat currency for crypto pair orders.';


-- Step 2: Create a new table to store details for option orders, following Option B (clean and precise).
CREATE TABLE public.account_order_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_order_id TEXT NOT NULL UNIQUE,
    option_ticker TEXT NOT NULL,
    option_type TEXT,
    strike_price NUMERIC,
    expiration_date DATE,
    is_mini_option BOOLEAN,
    underlying_security_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_account_order
        FOREIGN KEY(account_order_id)
        REFERENCES public.account_orders(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_underlying_security
        FOREIGN KEY(underlying_security_id)
        REFERENCES public.securities(id)
        ON DELETE SET NULL
);

COMMENT ON TABLE public.account_order_options IS 'Stores detailed information for options-based trading orders.';
COMMENT ON COLUMN public.account_order_options.account_order_id IS 'FK to account_orders.id, creating a one-to-one relationship.';
COMMENT ON COLUMN public.account_order_options.underlying_security_id IS 'FK to the underlying security in the securities table.';

-- Step 3: Enable RLS for the new table.
ALTER TABLE public.account_order_options ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow users to manage their own order options"
ON public.account_order_options
FOR ALL
USING (auth.uid() = get_user_id_from_account((SELECT account_id FROM public.account_orders WHERE id = account_order_id)))
WITH CHECK (auth.uid() = get_user_id_from_account((SELECT account_id FROM public.account_orders WHERE id = account_order_id)));

-- Step 4: Add a trigger for the new table's updated_at timestamp.
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON public.account_order_options
FOR EACH ROW
EXECUTE PROCEDURE public.trigger_set_timestamp();
