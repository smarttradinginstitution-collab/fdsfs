-- Enum Type for Folder Type
CREATE TYPE folder_type AS ENUM ('USER', 'SYSTEM');

-- Table for Notebook Folders
CREATE TABLE public.notebook_folders (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    general_account_id uuid NOT NULL,
    name text NOT NULL,
    folder_type folder_type NOT NULL DEFAULT 'USER'::folder_type,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT notebook_folders_pkey PRIMARY KEY (id),
    CONSTRAINT notebook_folders_general_account_id_fkey FOREIGN KEY (general_account_id) REFERENCES public.general_accounts(id) ON DELETE CASCADE,
    CONSTRAINT uq_notebook_folders_name_per_account UNIQUE (general_account_id, name)
);

-- Table for Notes
CREATE TABLE public.notes (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    folder_id uuid NOT NULL,
    general_account_id uuid NOT NULL,
    trade_id uuid, -- Nullable, for future use
    title text NOT NULL,
    content jsonb, -- For Tiptap editor content
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT notes_pkey PRIMARY KEY (id),
    CONSTRAINT notes_folder_id_fkey FOREIGN KEY (folder_id) REFERENCES public.notebook_folders(id) ON DELETE CASCADE,
    CONSTRAINT notes_general_account_id_fkey FOREIGN KEY (general_account_id) REFERENCES public.general_accounts(id) ON DELETE CASCADE,
    CONSTRAINT notes_trade_id_fkey FOREIGN KEY (trade_id) REFERENCES public.trades(id) ON DELETE SET NULL -- If a trade is deleted, the note is kept but the link is removed
);

-- Add comments to explain the design choices
COMMENT ON COLUMN public.notes.trade_id IS 'Nullable foreign key to link a note to a specific trade. Optional.';
COMMENT ON COLUMN public.notes.content IS 'Stores the rich text content from the Tiptap editor in JSONB format.';
COMMENT ON CONSTRAINT notes_trade_id_fkey ON public.notes IS 'When a trade is deleted, the note itself is not deleted, only the association is removed (SET NULL).';
COMMENT ON CONSTRAINT notebook_folders_general_account_id_fkey ON public.notebook_folders IS 'When a general account is deleted, all its associated folders are deleted as well.';
COMMENT ON CONSTRAINT notes_folder_id_fkey ON public.notes IS 'When a folder is deleted, all its notes are deleted as well.';
COMMENT ON CONSTRAINT uq_notebook_folders_name_per_account ON public.notebook_folders IS 'Ensures that each folder has a unique name within the same general account.';