-- Add parent_trade_id to trades table
ALTER TABLE public.trades
ADD COLUMN parent_trade_id UUID REFERENCES public.trades(id) ON DELETE SET NULL;

CREATE INDEX idx_trades_parent_trade_id ON public.trades(parent_trade_id);

-- Add grouping_tolerance to import_runs table
ALTER TABLE public.import_runs
ADD COLUMN grouping_tolerance INTEGER;
