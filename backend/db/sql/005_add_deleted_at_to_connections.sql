-- Add deleted_at for soft-delete functionality on brokerage_connections
ALTER TABLE public.brokerage_connections
ADD COLUMN deleted_at TIMESTAMPTZ;
