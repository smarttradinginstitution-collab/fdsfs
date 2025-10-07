-- migration_add_images_table.sql

CREATE TABLE public.images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    general_account_id UUID NOT NULL,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL UNIQUE,
    url VARCHAR NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_images_general_account
        FOREIGN KEY(general_account_id)
        REFERENCES public.general_accounts(id)
        ON DELETE CASCADE
);

-- Crea un indice sulla colonna general_account_id per velocizzare le ricerche
CREATE INDEX ix_images_general_account_id ON public.images (general_account_id);

-- Opzionale: se non hai già una funzione per aggiornare automaticamente
-- il timestamp 'updated_at', puoi usare questa.
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp_images
BEFORE UPDATE ON public.images
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();