-- PERMETTE DI COSTRUIRE UN PLAYBOOK A BLOCCHI (TESTO, GALLERIA, CONDIZIONI, ECC.)
CREATE TYPE playbook_block_type AS ENUM (
  'THESIS',       -- Testo ricco (la logica)
  'GALLERY',      -- Una galleria di immagini
  'CONDITIONS',   -- Il nuovo sistema di regole-dati
  'PSYCHOLOGY',   -- Note sullo stato mentale
  'LEGACY_RULES'  -- Per compatibilità con il tuo vecchio sistema
);

CREATE TABLE public.playbook_blocks (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  playbook_id uuid NOT NULL REFERENCES public.playbooks(id) ON DELETE CASCADE,
  block_type playbook_block_type NOT NULL,
  content jsonb,  -- Per 'THESIS' (JSON editor), 'PSYCHOLOGY' (note)
  "order" integer,
  created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- QUESTA È LA TABELLA PIÙ IMPORTANTE. SOSTITUISCE 'rules_playbook.rule' (text).
CREATE TABLE public.playbook_conditions (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  playbook_id uuid NOT NULL REFERENCES public.playbooks(id) ON DELETE CASCADE,
  category text NOT NULL,        -- Es: 'Market', 'Technical', 'Time'
  variable text NOT NULL,        -- Es: 'VIX', 'SPY_vs_200SMA', 'TimeOfDay'
  operator text NOT NULL,        -- Es: '>', '<', 'BETWEEN'
  "value" jsonb NOT NULL,        -- Es: {"value": 20} o {"min": "09:30", "max": "10:00"}
  "order" integer,
  created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- REGISTRA SE UNA CONDIZIONE È STATA RISPETTATA PER UN TRADE
CREATE TABLE public.trade_condition_checks (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  trade_id uuid NOT NULL REFERENCES public.trades(id) ON DELETE CASCADE,
  condition_id uuid NOT NULL REFERENCES public.playbook_conditions(id) ON DELETE CASCADE,
  was_met boolean NOT NULL,
  live_value text,               -- Valore opzionale: (es. VIX era '22' al momento del trade)
  created_at timestamp with time zone NOT NULL DEFAULT now()
);
