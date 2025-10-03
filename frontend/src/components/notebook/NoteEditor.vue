<template>
  <div v-if="note" class="note-editor-container">
    <div class="editor-header">
      <input v-model="editableTitle" class="title-input" />
      <div class="actions">
        <button @click="saveNote" class="button-save">Save</button>
        <button @click="cancelEdit" class="button-cancel">Cancel</button>
      </div>
    </div>
    <editor-content :editor="editor" class="tiptap-editor" />
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from 'vue';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import { useNotebookStore } from '../../stores/notebookStore';

const store = useNotebookStore();
const note = store.selectedNote;

const editableTitle = ref(note ? note.title : '');

const editor = useEditor({
  content: note ? note.content : '',
  extensions: [StarterKit],
  editorProps: {
    attributes: {
      class: 'prose prose-invert focus:outline-none',
    },
  },
});

watch(() => store.selectedNote, (newNote) => {
  if (newNote && editor.value) {
    editableTitle.value = newNote.title;
    // Check if content is different to avoid unnecessary updates and cursor jumps
    if (JSON.stringify(newNote.content) !== JSON.stringify(editor.value.getJSON())) {
        editor.value.commands.setContent(newNote.content);
    }
  }
});

const saveNote = async () => {
    if (!editor.value) return;
    try {
        await store.updateNote(note.id, {
            title: editableTitle.value,
            content: editor.value.getJSON(),
        });
        store.deselectNote(); // Go back to the list view
    } catch (error) {
        console.error("Failed to save note:", error);
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

.button-save, .button-cancel {
    padding: 0.5rem 1rem;
    border-radius: var(--semantic-border-radius-interactive);
    cursor: pointer;
    border: none;
}

.button-save {
    background-color: var(--semantic-color-interactive-primary-default);
    color: white;
}

.button-cancel {
    background-color: var(--semantic-color-surface-secondary);
    color: var(--semantic-color-text-primary);
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