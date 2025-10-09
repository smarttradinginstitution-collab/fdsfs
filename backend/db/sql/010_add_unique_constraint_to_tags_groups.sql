-- Aggiunge un vincolo di unicità alla tabella tags_groups per garantire che il nome
-- di un gruppo di tag sia unico all'interno di un singolo general_account.
ALTER TABLE public.tags_groups
ADD CONSTRAINT uq_tags_groups_name_general_account_id UNIQUE (name, general_account_id);