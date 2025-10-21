-- Aggiunge un indice sulla colonna user_id della tabella user_roles
-- Questo è fondamentale per accelerare la query che recupera i ruoli di un utente,
-- che viene eseguita su quasi ogni richiesta API protetta.
CREATE INDEX IF NOT EXISTS ix_public_user_roles_user_id ON public.user_roles (user_id);
