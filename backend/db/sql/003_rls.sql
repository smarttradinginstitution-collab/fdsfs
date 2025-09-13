-- Abilita RLS per le tabelle principali
ALTER TABLE public.trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trades_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_dashboard_layouts ENABLE ROW LEVEL SECURITY;

-- Policy per i TRADES: gli utenti possono vedere/modificare solo i propri trade
CREATE POLICY "trades_user_isolation" ON public.trades
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Policy per i TAGS: gli utenti possono vedere/modificare solo i propri tag
CREATE POLICY "tags_user_isolation" ON public.tags
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Policy per la tabella ponte TRADES_TAGS
CREATE POLICY "trades_tags_user_isolation" ON public.trades_tags
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Policy per USER_DASHBOARD_LAYOUTS
CREATE POLICY "user_dashboard_layouts_user_isolation" ON public.user_dashboard_layouts
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
