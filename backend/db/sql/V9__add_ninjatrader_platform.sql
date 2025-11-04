-- V9__add_ninjatrader_platform.sql
INSERT INTO public.platforms (name)
VALUES ('NinjaTrader 8')
ON CONFLICT (name) DO NOTHING;
