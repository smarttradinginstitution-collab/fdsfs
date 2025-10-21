-- V5__add_notebook_indexes.sql
-- Questo script aggiunge indici critici per migliorare le performance delle query
-- sulle tabelle notebook_folders e notes. Vengono creati indici parziali
-- per escludere le righe "soft-deleted".

-- Indice su general_account_id in notebook_folders per accelerare il recupero delle cartelle per utente.
CREATE INDEX IF NOT EXISTS idx_notebook_folders_general_account_id ON public.notebook_folders (general_account_id)
WHERE deleted_at IS NULL;

-- Indice su folder_id in notes per accelerare il recupero delle note all'interno di una cartella.
CREATE INDEX IF NOT EXISTS idx_notes_folder_id ON public.notes (folder_id)
WHERE deleted_at IS NULL;
