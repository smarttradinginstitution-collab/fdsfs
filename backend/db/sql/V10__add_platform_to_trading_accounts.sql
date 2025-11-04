-- V10__add_platform_to_trading_accounts.sql
ALTER TABLE public.trading_accounts
ADD COLUMN platform_id UUID;

ALTER TABLE public.trading_accounts
ADD CONSTRAINT fk_trading_accounts_platform
FOREIGN KEY (platform_id)
REFERENCES public.platforms(id)
ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_trading_accounts_platform_id
ON public.trading_accounts(platform_id);
