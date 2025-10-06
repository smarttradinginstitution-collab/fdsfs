-- Questo script rimuove la colonna `general_account_id` dalla tabella `notes`.
-- Questa colonna è ridondante perché l'associazione con il general_account
-- può essere derivata tramite la `notebook_folder` a cui la nota appartiene.

ALTER TABLE public.notes DROP COLUMN general_account_id;