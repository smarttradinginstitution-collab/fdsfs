<template>
  <div v-if="note" class="note-editor-container">
    <div class="editor-header">
      <input v-model="editableTitle" class="title-input" />
      <div class="actions">
        <span class="save-status">{{ saveStatus }}</span>
        <!-- The "Save as Template" button is hidden but its functionality is preserved -->
        <button @click="saveAsTemplate" class="button-secondary" v-show="false">Save as Template</button>
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
const saveStatus = ref(''); // To provide visual feedback on save state.

const editor = useEditor({
  content: note.value ? note.value.content : '',
  extensions: [StarterKit],
  editorProps: {
    attributes: {
      class: 'prose prose-invert focus:outline-none',
    },
  },
});

// Helper for debouncing
function debounce(fn, delay) {
  let timeoutId;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

watch(note, (newNote) => {
  if (newNote && editor.value) {
    editableTitle.value = newNote.title;
    // Avoid re-setting content if it's the same, to prevent cursor jumps
    if (JSON.stringify(newNote.content) !== JSON.stringify(editor.value.getJSON())) {
        editor.value.commands.setContent(newNote.content, false);
    }
  }
}, { deep: true });

const saveNote = async () => {
    if (!editor.value || !note.value) return;
    saveStatus.value = 'Saving...';
    try {
        await store.updateNote(note.value.id, {
            title: editableTitle.value,
            content: editor.value.getJSON(),
        });
        saveStatus.value = 'Saved!';
        // Clear the status message after a couple of seconds
        setTimeout(() => {
            saveStatus.value = '';
        }, 2000);
    } catch (error) {
        console.error("Failed to save note:", error);
        saveStatus.value = 'Error!';
    }
};

const debouncedSave = debounce(saveNote, 1500);

watch(editableTitle, (newTitle) => {
    if (note.value && newTitle !== note.value.title) {
        debouncedSave();
    }
});

watch(() => editor.value?.getHTML(), (newContent, oldContent) => {
    // Trigger save only on actual changes
    if (newContent !== oldContent && note.value) {
        debouncedSave();
    }
}, { deep: true });


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
    align-items: center;
    gap: 0.5rem;
}

.save-status {
    font-size: 0.875rem;
    color: var(--semantic-color-text-secondary);
    min-width: 80px; // Reserve space to prevent layout shift
    text-align: right;
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