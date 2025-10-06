-- db/sql/008_create_request_logs_table.sql

-- Creazione della tabella per memorizzare i log delle richieste HTTP
CREATE TABLE IF NOT EXISTS public.request_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    method VARCHAR(10) NOT NULL,
    path TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Indici per migliorare le performance delle query
CREATE INDEX IF NOT EXISTS idx_request_logs_path ON public.request_logs(path);
CREATE INDEX IF NOT EXISTS idx_request_logs_status_code ON public.request_logs(status_code);
CREATE INDEX IF NOT EXISTS idx_request_logs_created_at ON public.request_logs(created_at);

-- Commenti sulla tabella e sulle colonne per chiarezza
COMMENT ON TABLE public.request_logs IS 'Tabella per il logging delle richieste HTTP al fine di monitorare le performance.';
COMMENT ON COLUMN public.request_logs.id IS 'Identificativo univoco del log.';
COMMENT ON COLUMN public.request_logs.method IS 'Metodo HTTP della richiesta (es. GET, POST).';
COMMENT ON COLUMN public.request_logs.path IS 'Path della richiesta (URL).';
COMMENT ON COLUMN public.request_logs.status_code IS 'Codice di stato HTTP della risposta.';
COMMENT ON COLUMN public.request_logs.response_time_ms IS 'Tempo di risposta del server in millisecondi.';
COMMENT ON COLUMN public.request_logs.created_at IS 'Timestamp di quando la richiesta è stata registrata.';