-- 008_create_brokerage_accounts_table.sql

-- Create the brokerage_accounts table to store trading account details
CREATE TABLE public.brokerage_accounts (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    connection_id uuid NOT NULL,
    name text NOT NULL,
    number text NOT NULL,
    balance numeric NOT NULL,
    currency text NOT NULL,
    institution_name text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT brokerage_accounts_pkey PRIMARY KEY (id),
    CONSTRAINT brokerage_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
    CONSTRAINT brokerage_accounts_connection_id_fkey FOREIGN KEY (connection_id) REFERENCES public.brokerage_connections(id) ON DELETE CASCADE
);

-- Add comments to the table and columns
COMMENT ON TABLE public.brokerage_accounts IS 'Stores detailed information for each trading account, synced from SnapTrade.';
COMMENT ON COLUMN public.brokerage_accounts.id IS 'The unique account ID from SnapTrade.';
COMMENT ON COLUMN public.brokerage_accounts.user_id IS 'Foreign key to public.profiles.id, identifying the user.';
COMMENT ON COLUMN public.brokerage_accounts.connection_id IS 'Foreign key to public.brokerage_connections.id, linking the account to a specific connection.';
COMMENT ON COLUMN public.brokerage_accounts.name IS 'The name of the trading account.';
COMMENT ON COLUMN public.brokerage_accounts.number IS 'The account number.';
COMMENT ON COLUMN public.brokerage_accounts.balance IS 'The total cash balance of the account.';
COMMENT ON COLUMN public.brokerage_accounts.currency IS 'The currency of the account balance.';
COMMENT ON COLUMN public.brokerage_accounts.institution_name IS 'The name of the brokerage or financial institution.';

-- Enable Row Level Security
ALTER TABLE public.brokerage_accounts ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to see their own accounts
CREATE POLICY "Allow users to see their own accounts"
ON public.brokerage_accounts
FOR SELECT
USING (auth.uid() = user_id);

-- Create policy to allow users to insert their own accounts
CREATE POLICY "Allow users to insert their own accounts"
ON public.brokerage_accounts
FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Create policy to allow users to update their own accounts
CREATE POLICY "Allow users to update their own accounts"
ON public.brokerage_accounts
FOR UPDATE
USING (auth.uid() = user_id);

-- Create policy to allow users to delete their own accounts
CREATE POLICY "Allow users to delete their own accounts"
ON public.brokerage_accounts
FOR DELETE
USING (auth.uid() = user_id);

-- This function will be reused for other tables to update the 'updated_at' timestamp
CREATE OR REPLACE FUNCTION public.trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update 'updated_at' on row update for brokerage_accounts
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON public.brokerage_accounts
FOR EACH ROW
EXECUTE PROCEDURE public.trigger_set_timestamp();
