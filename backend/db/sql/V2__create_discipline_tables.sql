-- 1. Tabella: discipline_rules (Il Template)
-- Questa tabella memorizza le regole che l'utente crea nel modale "Edit Rules".
CREATE TABLE public.discipline_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    general_account_id UUID NOT NULL REFERENCES public.general_accounts(id) ON DELETE CASCADE,

    rule_type TEXT NOT NULL, -- 'AUTOMATED' o 'MANUAL'
    name TEXT NOT NULL, -- Es: "Max loss per trade" o "100 Press-ups"
    description TEXT,

    -- Campi per le condizioni delle regole
    condition_type TEXT, -- 'TIME', 'PERCENTAGE', 'FIXED_AMOUNT', 'PERCENTAGE_OR_FIXED'
    condition_value JSONB, -- Es: {"time": "12:00"}, {"percentage": 100}, {"amount": 4000}

    -- Programmazione per i giorni della settimana
    active_days INT[] NOT NULL, -- Es: [1,2,3,4,5] per Lun-Ven

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Tabella: daily_rule_instances (La Checklist del Giorno)
-- Questa è la tabella chiave. Quando un utente inizia la giornata,
-- il sistema copia le sue regole da discipline_rules qui.
CREATE TABLE public.daily_rule_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_journal_id UUID NOT NULL REFERENCES public.notes(id) ON DELETE CASCADE,
    rule_template_id UUID REFERENCES public.discipline_rules(id) ON DELETE SET NULL, -- La regola originale

    name TEXT NOT NULL, -- Nome della regola (copiato)
    rule_type TEXT NOT NULL, -- 'AUTOMATED' o 'MANUAL' (copiato)

    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'completed', 'failed'

    -- Risultato effettivo per confronto
    actual_value TEXT, -- Es: "1/1", "0/1", "$500 / $4000"

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);