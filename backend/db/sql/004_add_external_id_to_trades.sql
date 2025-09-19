-- Questo script aggiorna la tabella 'trades' per supportare l'importazione CSV idempotente.

-- 1. Aggiunge la colonna 'external_id' per memorizzare l'identificativo univoco
--    del trade proveniente da fonti esterne (es. 'Trade #' da un file CSV).
--    La colonna permette valori NULL perché i trade esistenti o creati manualmente
--    potrebbero non avere un ID esterno.
ALTER TABLE public.trades
ADD COLUMN external_id VARCHAR;

-- 2. Aggiunge un indice sulla nuova colonna per ottimizzare le performance
--    delle query che filtrano o cercano per 'external_id'.
CREATE INDEX idx_trades_external_id ON public.trades(external_id);

-- 3. Aggiunge un vincolo di unicità sulla combinazione di 'user_id' e 'external_id'.
--    Questo è il vincolo chiave che garantisce l'idempotenza: impedisce
--    l'inserimento di un trade con un 'external_id' che esiste già per lo stesso utente.
--    PostgreSQL considera i valori NULL come unici, quindi più trade senza
--    'external_id' possono coesistere per lo stesso utente.
ALTER TABLE public.trades
ADD CONSTRAINT uq_user_external_id UNIQUE (user_id, external_id);

-- NOTA: Questo script è pensato per essere eseguito una sola volta.
-- Se eseguito più volte, genererà errori (es. "colonna già esistente").
