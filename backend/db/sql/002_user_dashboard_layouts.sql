-- db/sql/002_user_dashboard_layouts.sql

CREATE TABLE IF NOT EXISTS public.user_dashboard_layouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    layout JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_dashboard_layouts_user_id UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_dashboard_layouts_user_id ON public.user_dashboard_layouts(user_id);
