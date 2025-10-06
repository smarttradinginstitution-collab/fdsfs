-- Crea la tabella dei mercati
CREATE TABLE public.asset_markets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL UNIQUE,
    code text UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Aggiungi la colonna di riferimento in assets
-- La colonna è nullable temporaneamente per permettere l'aggiornamento dei dati esistenti
ALTER TABLE public.assets ADD COLUMN asset_market_id uuid;

-- Crea la relazione (foreign key)
ALTER TABLE public.assets ADD CONSTRAINT assets_asset_market_id_fkey FOREIGN KEY (asset_market_id) REFERENCES public.asset_markets(id);

-- Inserisci un mercato di default per gli asset esistenti
INSERT INTO public.asset_markets (name, code) VALUES ('Unknown', 'UNKNOWN');

-- Aggiorna tutti gli asset esistenti per usare il mercato di default
UPDATE public.assets
SET asset_market_id = (SELECT id FROM public.asset_markets WHERE code = 'UNKNOWN')
WHERE asset_market_id IS NULL;

-- Rendi la colonna NOT NULL dopo aver aggiornato i dati esistenti
ALTER TABLE public.assets ALTER COLUMN asset_market_id SET NOT NULL;

-- Abilita RLS
ALTER TABLE public.asset_markets ENABLE ROW LEVEL SECURITY;

-- Policy per la lettura (utenti autenticati)
CREATE POLICY "Allow authenticated users to read asset markets"
ON public.asset_markets
FOR SELECT
TO authenticated
USING (true);

-- Policy per la creazione (solo admin)
CREATE POLICY "Allow admin users to create asset markets"
ON public.asset_markets
FOR INSERT
TO authenticated
WITH CHECK (is_admin(auth.uid()));

-- Policy per l'aggiornamento (solo admin)
CREATE POLICY "Allow admin users to update asset markets"
ON public.asset_markets
FOR UPDATE
TO authenticated
USING (is_admin(auth.uid()))
WITH CHECK (is_admin(auth.uid()));

-- Policy per la cancellazione (solo admin)
CREATE POLICY "Allow admin users to delete asset markets"
ON public.asset_markets
FOR DELETE
TO authenticated
USING (is_admin(auth.uid()));