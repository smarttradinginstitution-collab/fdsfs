-- 002_user_dashboard_layouts.sql

-- Funzione per aggiornare updated_at
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Tabella per memorizzare i layout della dashboard personalizzati degli utenti
CREATE TABLE IF NOT EXISTS public.user_dashboard_layouts (
    user_id UUID PRIMARY KEY,
    layout_config JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES auth.users(id)
        ON DELETE CASCADE
);

-- Trigger per aggiornare automaticamente updated_at
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON public.user_dashboard_layouts
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Commenti per chiarire lo scopo della tabella e delle colonne
COMMENT ON TABLE public.user_dashboard_layouts IS 'Stores the personalized dashboard layout for each user.';
COMMENT ON COLUMN public.user_dashboard_layouts.user_id IS 'The ID of the user, referencing auth.users.';
COMMENT ON COLUMN public.user_dashboard_layouts.layout_config IS 'The JSON configuration of the user''s dashboard grid layout.';
COMMENT ON COLUMN public.user_dashboard_layouts.created_at IS 'Timestamp of when the layout was first created.';
COMMENT ON COLUMN public.user_dashboard_layouts.updated_at IS 'Timestamp of when the layout was last updated.';
