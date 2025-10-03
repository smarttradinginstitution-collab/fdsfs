<template>
  <div v-if="note" class="note-editor-container">
    <div class="editor-header">
      <input v-model="editableTitle" class="title-input" />
      <div class="actions">
        <button @click="saveNote" class="button-save">Save</button>
        <button @click="saveAsTemplate" class="button-secondary">Save as Template</button>
        <button @click="cancelEdit" class="button-cancel">Cancel</button>
      </div>
    </div>
    <editor-content :editor="editor" class="tiptap-editor" />
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import { useNotebookStore } from '../../stores/notebookStore';

const store = useNotebookStore();
const note = computed(() => store.selectedNote);

const editableTitle = ref(note.value ? note.value.title : '');

const editor = useEditor({
  content: note.value ? note.value.content : '',
  extensions: [StarterKit],
  editorProps: {
    attributes: {
      class: 'prose prose-invert focus:outline-none',
    },
  },
});

watch(note, (newNote) => {
  if (newNote && editor.value) {
    editableTitle.value = newNote.title;
    if (JSON.stringify(newNote.content) !== JSON.stringify(editor.value.getJSON())) {
        editor.value.commands.setContent(newNote.content, false);
    }
  }
}, { deep: true });


const saveNote = async () => {
    if (!editor.value || !note.value) return;
    try {
        await store.updateNote(note.value.id, {
            title: editableTitle.value,
            content: editor.value.getJSON(),
        });
        store.deselectNote();
    } catch (error) {
        console.error("Failed to save note:", error);
    }
};

const saveAsTemplate = async () => {
    if (!editor.value || !note.value) return;
    if (confirm("Save the current content as the template for this folder? This will overwrite any existing template.")) {
        try {
            await store.saveFolderTemplate({
                folderId: note.value.folder_id,
                templateContent: editor.value.getJSON(),
            });
            // Optionally, show a success toast
        } catch (error) {
            console.error("Failed to save template:", error);
        }
    }
};

const cancelEdit = () => {
    store.deselectNote();
};

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy();
  }
});
</script>

<style lang="scss">
.note-editor-container {
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.title-input {
    font-size: 1.5rem;
    font-weight: bold;
    background: transparent;
    border: none;
    color: var(--semantic-color-text-primary);
    width: 70%;
    &:focus {
        outline: none;
        border-bottom: 1px solid var(--semantic-color-border-default);
    }
}

.actions {
    display: flex;
    gap: 0.5rem;
}

.button-save, .button-cancel, .button-secondary {
    padding: 0.5rem 1rem;
    border-radius: var(--semantic-border-radius-interactive);
    cursor: pointer;
    border: 1px solid transparent;
    transition: background-color 0.2s;
}

.button-save {
    background-color: var(--semantic-color-interactive-primary-default);
    color: white;
    border-color: transparent;
}

.button-cancel, .button-secondary {
    background-color: var(--semantic-color-surface-secondary);
    color: var(--semantic-color-text-primary);
    border-color: var(--semantic-color-border-default);
}

.button-cancel:hover, .button-secondary:hover {
    background-color: var(--semantic-color-surface-tertiary);
}

.tiptap-editor {
    flex-grow: 1;
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-interactive);
    padding: 1rem;
    overflow-y: auto;
}

/* Tiptap default styles override */
.prose {
    max-width: none;
}
</style>