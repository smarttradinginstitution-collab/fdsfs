-- 1. Cancella i blocchi esistenti (visto che hai detto che si può fare)
DELETE FROM public.playbook_blocks;

-- 2. Droppa il vecchio tipo (se esiste) e ricrealo pulito
DROP TYPE IF EXISTS public.playbook_block_type CASCADE;
DROP TYPE IF EXISTS public.block_type_enum CASCADE; -- Drop new name too just in case

-- 3. Crea i "Fantastici 3" definitivi
CREATE TYPE public.block_type_enum AS ENUM (
  'RULES',      -- Il motore (Conditions, Checklist, Gruppi)
  'THESIS',     -- Il cervello (Testo ricco, Spiegazioni)
  'GALLERY'     -- Gli occhi (Screenshot A+, Anti-pattern)
);

-- 4. Assicurati che la tabella usi questo nuovo tipo
-- First, drop the old column if it exists
ALTER TABLE public.playbook_blocks DROP COLUMN IF EXISTS block_type;
-- Now, add the new column with the correct enum type
ALTER TABLE public.playbook_blocks
ADD COLUMN block_type public.block_type_enum NOT NULL DEFAULT 'RULES';
