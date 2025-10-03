-- Add a column to store the Tiptap JSON content for note templates
ALTER TABLE public.notebook_folders
ADD COLUMN template_content jsonb;

-- Add a comment to explain the purpose of the new column
COMMENT ON COLUMN public.notebook_folders.template_content IS 'Stores the rich text content from the Tiptap editor to be used as a template for new notes in this folder.';