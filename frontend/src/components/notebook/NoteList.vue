<template>
  <BaseWidget class="note-list-widget">
    <!-- Header: Title and "Log Day" action -->
    <template #header>
      <div class="header-content">
        <h2 class="header-title" v-if="store.selectedFolder">{{ store.selectedFolder.name }}</h2>
        <div class="spacer"></div>
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
      <div v-if="store.selectedFolder" class="content-wrapper">
        <div v-if="store.isLoadingNotes" class="loading-spinner">Loading...</div>
        <div v-else-if="store.error" class="error-message">{{ store.error }}</div>

        <ul v-else-if="store.filteredNotes.length > 0" class="notes">
          <li
            v-for="note in store.filteredNotes"
            :key="note.id"
            @click="selectNote(note.id)"
            class="note-item"
            :class="{ 'is-selected': store.selectedNoteId === note.id }"
          >
            <div class="note-text-content">
              <h3 class="note-title">{{ note.title }}</h3>
              <p class="note-preview">{{ generatePreview(note.content) }}</p>
            </div>
            <button @click.stop="handleDeleteNote(note.id)" class="delete-button" aria-label="Delete note">
              <TrashIcon />
            </button>
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
import { CalendarIcon, TrashIcon } from '@heroicons/vue/24/outline';

const store = useNotebookStore();
const logDayDate = ref(null);

const selectNote = (noteId) => {
  store.selectNote(noteId);
};

const handleLogDay = async (date) => {
  if (!date || !store.selectedFolderId) return;

  const noteTitle = date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  try {
    const newNote = await store.createNote({
      folder_id: store.selectedFolderId,
      title: noteTitle,
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
    });
    if (newNote && newNote.id) {
      store.selectNote(newNote.id);
    }
  } catch (error) {
    console.error("Error logging day from component:", error);
  }

  logDayDate.value = null;
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

const generatePreview = (content) => {
  if (!content || !content.content) return '';
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
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }
}

.header-content {
  display: flex;
  align-items: center;
  width: 100%;
  gap: var(--semantic-size-stack-sm);
}

.header-title {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.spacer {
  flex-grow: 1;
}

.log-day-button {
  font: var(--semantic-font-style-label-md-bold);
  color: var(--semantic-color-text-interactive);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--semantic-size-stack-xxs);
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-xs);
  flex-shrink: 0; /* Prevent the button from shrinking */

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
  padding: var(--semantic-size-inset-sm);
  width: 100%;
}

.notes {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xxs); /* Compact gap */
}

.note-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--semantic-size-inset-sm); /* Compact padding */
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
  text-align: left;
  border-bottom: 1px solid var(--semantic-color-border-default);

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

.note-text-content {
  flex-grow: 1;
  min-width: 0;
}

.note-title {
  font: var(--semantic-font-style-label-sm); /* Compact font */
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-xxs);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.note-preview {
  font: var(--semantic-font-style-body-xs); /* Compact font */
  color: var(--semantic-color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delete-button {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  padding: var(--semantic-size-stack-xxs);
  flex-shrink: 0;
  margin-left: var(--semantic-size-stack-xs);
  opacity: 0.5;
  transition: opacity 0.15s ease-in-out;

  &:hover {
    color: var(--semantic-color-text-danger);
    opacity: 1;
  }

  svg {
    width: 1rem;
    height: 1rem;
  }
}

.empty-state,
.empty-state-no-folder,
.loading-spinner {
  text-align: center;
  padding: var(--semantic-size-stack-xl) var(--semantic-size-inset-md);
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