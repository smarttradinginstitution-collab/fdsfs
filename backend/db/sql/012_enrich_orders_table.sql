-- Add new columns to the account_orders table to store enriched data from the /orders endpoint
ALTER TABLE public.account_orders
ADD COLUMN order_type TEXT,
ADD COLUMN time_in_force TEXT,
ADD COLUMN stop_price NUMERIC;
