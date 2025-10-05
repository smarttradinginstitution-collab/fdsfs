<template>
  <BaseWidget class="note-list-widget">
    <!-- Header: "Log Day" action -->
    <template #header>
      <div class="header-content">
        <VueDatePicker
          v-model="logDayDate"
          @update:model-value="handleLogDay"
          :enable-time-picker="false"
          auto-apply
          dark
          :teleport="true"
          :disabled="!store.selectedFolderId"
          class="log-day-picker"
        >
          <template #trigger>
            <button class="log-day-button" :disabled="!store.selectedFolderId">
              <CalendarIcon class="icon" />
              <span>Log Day</span>
            </button>
          </template>
        </VueDatePicker>
      </div>
    </template>

    <!-- Main Content: Note List -->
    <div class="note-list-container">
      <div v-if="store.selectedFolder">
        <div v-if="store.isLoadingNotes" class="loading-spinner">Loading notes...</div>
        <div v-else-if="store.error" class="error-message">{{ store.error }}</div>

        <ul v-else-if="store.filteredNotes.length > 0" class="notes">
          <li
            v-for="note in store.filteredNotes"
            :key="note.id"
            @click="selectNote(note.id)"
            class="note-item"
            :class="{ 'is-selected': store.selectedNoteId === note.id }"
          >
            <h3 class="note-title">{{ note.title }}</h3>
            <p class="note-preview">{{ generatePreview(note.content) }}</p>
            <div class="note-footer">
              <span class="note-date">{{ new Date(note.updated_at).toLocaleDateString() }}</span>
              <button @click.stop="handleDeleteNote(note.id)" class="delete-button">🗑️</button>
            </div>
          </li>
        </ul>
        <div v-else class="empty-state">
          <p v-if="store.searchQuery">No notes match your search.</p>
          <p v-else>This folder is empty. Use "Log Day" to add a new note.</p>
        </div>
      </div>
      <div v-else class="empty-state-no-folder">
        <p>Select a folder to see your notes.</p>
      </div>
    </div>
  </BaseWidget>
</template>

<script setup>
import { ref } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import BaseWidget from '../layout/BaseWidget.vue';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { CalendarIcon } from '@heroicons/vue/24/outline';

const store = useNotebookStore();
const logDayDate = ref(null);

const selectNote = (noteId) => {
  store.selectNote(noteId);
};

const handleLogDay = async (date) => {
  if (!date || !store.selectedFolderId) return;

  const defaultTitle = date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const noteTitle = prompt("Enter a title for the new note:", defaultTitle);

  if (noteTitle && noteTitle.trim()) {
    try {
      const newNote = await store.createNote({
        folder_id: store.selectedFolderId,
        title: noteTitle.trim(),
        content: { type: 'doc', content: [{ type: 'paragraph' }] },
      });
      // Automatically select the new note to open it in the editor
      if (newNote && newNote.id) {
        store.selectNote(newNote.id);
      }
    } catch (error) {
      console.error("Error logging day from component:", error);
    }
  }

  logDayDate.value = null; // Reset picker
};

const handleDeleteNote = async (noteId) => {
    if (confirm('Are you sure you want to delete this note?')) {
        try {
            await store.deleteNote(noteId);
        } catch (error) {
            console.error("Failed to delete note:", error);
        }
    }
};

// A simple function to generate a text preview from Tiptap's JSON content
const generatePreview = (content) => {
    if (!content || !content.content) return 'No content';
    let text = '';
    content.content.forEach(node => {
        if (node.type === 'paragraph' && node.content) {
            node.content.forEach(textNode => {
                if (textNode.type === 'text') {
                    text += textNode.text + ' ';
                }
            });
        }
    });
    return text.trim().slice(0, 100) + (text.length > 100 ? '...' : '');
};
</script>

<style lang="scss" scoped>
.note-list-widget {
  :deep(.widget-content) {
    padding: 0;
  }
}

.header-content {
  display: flex;
  justify-content: flex-end; /* Align button to the right */
  align-items: center;
  width: 100%;
}

.log-day-button {
  font: var(--semantic-font-style-label-md-bold);
  color: var(--semantic-color-text-interactive);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover:not(:disabled) {
    text-decoration: underline;
  }
  &:disabled {
    color: var(--semantic-color-text-disabled);
    cursor: not-allowed;
  }

  .icon {
    width: 1.25rem;
    height: 1.25rem;
  }
}

.note-list-container {
  padding: 1rem;
  height: 100%;
  overflow-y: auto;
}

.notes {
  list-style: none;
  padding: 0;
  margin: 0;
}

.note-item {
  padding: 1rem;
  border-bottom: 1px solid var(--semantic-color-border-default);
  cursor: pointer;
  transition: background-color 0.2s;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
  }

  &.is-selected {
    background-color: var(--semantic-color-surface-selected);
  }
}

.note-title {
  font: var(--semantic-font-style-label-lg-bold);
  color: var(--semantic-color-text-primary);
  margin-bottom: 0.25rem;
}

.note-preview {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  margin-bottom: 0.5rem;
  // Truncate preview text
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: var(--semantic-color-text-secondary);
}

.delete-button {
  background: none;
  border: none;
  color: var(--semantic-color-text-danger);
  cursor: pointer;
  padding: 0.25rem;
}

.empty-state,
.empty-state-no-folder,
.loading-spinner {
  text-align: center;
  padding-top: 4rem;
  color: var(--semantic-color-text-secondary);
}

.log-day-picker {
  :global(.dp__theme_dark) {
    --dp-background-color: var(--semantic-color-surface-secondary);
    --dp-text-color: var(--semantic-color-text-primary);
    --dp-hover-color: var(--semantic-color-surface-tertiary);
    --dp-hover-text-color: var(--semantic-color-text-primary);
    --dp-primary-color: var(--semantic-color-interactive-primary-default);
    --dp-primary-text-color: var(--semantic-color-text-on-primary);
    --dp-border-color: var(--semantic-color-border-default);
    --dp-border-color-hover: var(--semantic-color-border-focus);
    --dp-icon-color: var(--semantic-color-text-secondary);
  }
}
</style>