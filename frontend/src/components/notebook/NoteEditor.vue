<template>
  <div v-if="note" class="note-editor-container">
    <!-- Note Title -->
    <input v-model="editableTitle" class="title-input" />

    <!-- Metadata Header -->
    <div class="metadata-header">
      <div class="meta-item">
        <strong>Created:</strong> {{ formatDate(note.created_at) }}
      </div>
      <div class="meta-item">
        <strong>Updated:</strong> {{ formatDate(note.updated_at) }}
      </div>
      <div class="meta-item pnl-item">
        <strong>Net P&L:</strong>
        <span :class="pnlClass(financialData?.net_pnl)">
          {{ formatCurrency(financialData?.net_pnl) }}
        </span>
      </div>
    </div>

    <!-- Financial Details Section (only for Trade Notes) -->
    <div v-if="isTradeNoteFolder" class="financial-details">
      <div class="detail-card">
        <label>Gross P&L</label>
        <span>{{ formatCurrency(financialData?.gross_pnl) }}</span>
      </div>
      <div class="detail-card">
        <label>Commissions</label>
        <span>{{ formatCurrency(financialData?.total_commissions) }}</span>
      </div>
      <div class="detail-card">
        <label>Net ROI</label>
        <span>{{ formatPercentage(financialData?.net_roi) }}</span>
      </div>
    </div>

    <!-- Editor Content -->
    <div class="editor-header-actions">
       <span class="save-status">{{ saveStatus }}</span>
       <button @click="saveAsTemplate" class="button-secondary" v-show="false">Save as Template</button>
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
const financialData = computed(() => store.financialData);
const folder = computed(() => store.selectedNoteFolder);

const isTradeNoteFolder = computed(() => folder.value?.name === 'Trade Notes');

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

// Helper functions for formatting
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const formatCurrency = (value) => {
  if (typeof value !== 'number') return 'N/A';
  return value.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  });
};

const formatPercentage = (value) => {
    if (typeof value !== 'number') return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
};

const pnlClass = (pnl) => {
  if (typeof pnl !== 'number') return 'pnl-neutral';
  return pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
};

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
  gap: 1rem; /* Add gap between all flex children */
}

.title-input {
    font-size: 1.8rem; /* Larger title */
    font-weight: bold;
    background: transparent;
    border: none;
    color: var(--semantic-color-text-primary);
    padding: 0.25rem 0;
    &:focus {
        outline: none;
        box-shadow: 0 1px 0 var(--semantic-color-border-focus);
    }
}

.metadata-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--semantic-color-text-secondary);
  flex-wrap: wrap;
}

.meta-item strong {
  color: var(--semantic-color-text-primary);
}

.pnl-item {
  font-weight: bold;
}
.pnl-positive {
  color: var(--semantic-color-text-success);
}
.pnl-negative {
  color: var(--semantic-color-text-danger);
}
.pnl-neutral {
  color: var(--semantic-color-text-secondary);
}

.financial-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  padding: 1rem;
  background-color: var(--semantic-color-surface-secondary);
  border-radius: var(--semantic-border-radius-container);
}

.detail-card {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-card label {
  font-size: 0.875rem;
  color: var(--semantic-color-text-secondary);
}

.detail-card span {
  font-size: 1.125rem;
  font-weight: 500;
  color: var(--semantic-color-text-primary);
}

.editor-header-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end; /* Align save status to the right */
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