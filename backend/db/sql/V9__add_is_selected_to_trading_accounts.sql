-- Aggiunge la colonna 'is_selected' alla tabella 'trading_accounts'
-- per tracciare quali account sono attivi per un utente.

ALTER TABLE public.trading_accounts
ADD COLUMN is_selected BOOLEAN NOT NULL DEFAULT false;
