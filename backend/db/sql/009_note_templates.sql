-- 1) Tabella dei template di nota
CREATE TABLE public.note_templates (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    general_account_id uuid NOT NULL,
    title text NOT NULL,
    "text" text,
    url_image text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT fk_note_templates_general_account FOREIGN KEY (general_account_id) REFERENCES public.general_accounts(id) ON DELETE CASCADE
);

-- (opzionale) Unicità titolo per account (toglia se vuoi titoli duplicati)
CREATE UNIQUE INDEX note_templates_unique_title_per_account ON public.note_templates(general_account_id, title);

-- Indice FK
CREATE INDEX note_templates_general_account_id_idx ON public.note_templates(general_account_id);

-- 2) Tabella ponte molti-a-molti Note <-> NoteTemplate
CREATE TABLE public.notes_note_templates (
    note_id uuid NOT NULL,
    note_template_id uuid NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT notes_note_templates_pkey PRIMARY KEY (note_id, note_template_id),

    CONSTRAINT fk_nnt_note FOREIGN KEY (note_id) REFERENCES public.notes(id) ON DELETE CASCADE,

    CONSTRAINT fk_nnt_template FOREIGN KEY (note_template_id) REFERENCES public.note_templates(id) ON DELETE CASCADE
);

-- Indici utili alla navigazione
CREATE INDEX nnt_note_id_idx ON public.notes_note_templates(note_id);
CREATE INDEX nnt_note_template_id_idx ON public.notes_note_templates(note_template_id);

-- 3) Trigger per coerenza cross-account (fortemente consigliato)
-- Verifica che la nota e il template appartengano allo stesso general_account.
-- Poiché la nota ha solo folder_id, risaliamo a notebook_folders -> general_accounts.
CREATE OR REPLACE FUNCTION public.ensure_note_and_template_same_account()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_note_account uuid;
    v_template_account uuid;
BEGIN
    -- general_account della nota (tramite la sua cartella)
    SELECT nf.general_account_id INTO v_note_account
    FROM public.notes n
    JOIN public.notebook_folders nf ON nf.id = n.folder_id
    WHERE n.id = NEW.note_id;

    IF v_note_account IS NULL THEN
        RAISE EXCEPTION 'Nota % non trovata o cartella non valida', NEW.note_id;
    END IF;

    -- general_account del template
    SELECT nt.general_account_id INTO v_template_account
    FROM public.note_templates nt
    WHERE nt.id = NEW.note_template_id;

    IF v_template_account IS NULL THEN
        RAISE EXCEPTION 'Template % non trovato', NEW.note_template_id;
    END IF;

    IF v_note_account <> v_template_account THEN
        RAISE EXCEPTION 'Nota e Template appartengono a general_account diversi (% <> %)', v_note_account, v_template_account;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_nnt_same_account
BEFORE INSERT OR UPDATE ON public.notes_note_templates
FOR EACH ROW EXECUTE FUNCTION public.ensure_note_and_template_same_account();

-- 4) (opzionale) trigger per aggiornare updated_at su note_templates
CREATE OR REPLACE FUNCTION public.touch_note_templates_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_note_templates_touch_updated_at
BEFORE UPDATE ON public.note_templates
FOR EACH ROW EXECUTE FUNCTION public.touch_note_templates_updated_at();