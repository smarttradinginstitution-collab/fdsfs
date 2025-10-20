-- Add index to notes.trade_id for faster lookups
CREATE INDEX IF NOT EXISTS ix_notes_trade_id ON public.notes (trade_id);
