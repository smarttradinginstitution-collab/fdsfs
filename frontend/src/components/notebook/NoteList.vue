<template>
  <BaseWidget class="note-list-widget">
    <!-- Header: Log Day -->
    <template #header>
      <div class="header-content">
        <VueDatePicker
          v-model="logDayDate"
          @update:model-value="handleLogDay"
          :enable-time-picker="false"
          auto-apply
          dark
          :teleport="true"
          placeholder="Log Day"
          class="log-day-picker"
        >
          <template #trigger>
            <button class="log-day-button">
              <CalendarDaysIcon class="icon" />
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

        <ul v-else-if="filteredNotes.length > 0" class="notes">
          <li
            v-for="note in filteredNotes"
            :key="note.id"
            @click="selectNote(note.id)"
            class="note-item"
            :class="{ 'is-selected': store.selectedNoteId === note.id }"
          >
            <h3 class="note-title">{{ note.title }}</h3>
            <p class="note-preview">{{ generatePreview(note.content) }}</p>
            <div class="note-footer">
              <span class="note-date">{{ new Date(note.updated_at).toLocaleDateString() }}</span>
              <button @click.stop="handleDeleteNote(note.id)" class="delete-button">
                <TrashIcon class="icon" />
              </button>
            </div>
          </li>
        </ul>
        <div v-else-if="searchQuery" class="empty-state">
          <p>No notes match your search.</p>
        </div>
        <div v-else class="empty-state">
          <p>This folder is empty.</p>
          <p>Click "Log Day" to create a new entry.</p>
        </div>
      </div>
      <div v-else class="empty-state-no-folder">
        <p>Select a folder to see your notes.</p>
      </div>
    </div>
  </BaseWidget>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import BaseWidget from '../layout/BaseWidget.vue';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { TrashIcon, CalendarDaysIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  searchQuery: {
    type: String,
    default: '',
  },
});

const store = useNotebookStore();
const logDayDate = ref(null);

const filteredNotes = computed(() => {
  if (!props.searchQuery) {
    return store.notes;
  }
  return store.notes.filter(
    (note) =>
      note.title.toLowerCase().includes(props.searchQuery.toLowerCase()) ||
      generatePreview(note.content).toLowerCase().includes(props.searchQuery.toLowerCase())
  );
});

const selectNote = (noteId) => {
  store.selectNote(noteId);
};

const handleLogDay = async (date) => {
  if (!date || !store.selectedFolderId) {
    // Maybe show a toast notification here to select a folder first
    alert('Please select a folder before logging a day.');
    return;
  }
  try {
    await store.logDay(date);
    logDayDate.value = null; // Reset picker
  } catch (error) {
    console.error('Error logging day from component:', error);
  }
};

const handleDeleteNote = async (noteId) => {
  if (confirm('Are you sure you want to delete this note?')) {
    try {
      await store.deleteNote(noteId);
    } catch (error) {
      console.error('Failed to delete note:', error);
    }
  }
};

const generatePreview = (content) => {
  if (!content || !content.content) return '';
  let text = '';
  content.content.forEach((node) => {
    if (node.type === 'paragraph' && node.content) {
      node.content.forEach((textNode) => {
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
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.log-day-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font: var(--semantic-font-style-label-lg);
  color: var(--semantic-color-text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;

  &:hover {
    color: var(--semantic-color-text-primary);
  }

  .icon {
    width: 1.25rem;
    height: 1.25rem;
  }
}

.note-list-container {
  padding: 1rem;
  height: 100%;
  width: 100%;
}

.notes {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.note-item {
  padding: 1rem;
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
  }

  &.is-selected {
    background-color: var(--semantic-color-surface-selected);
    border-color: var(--semantic-color-border-focus);
  }
}

.note-title {
  font: var(--semantic-font-style-heading-xs);
  color: var(--semantic-color-text-primary);
  margin-bottom: 0.5rem;
}

.note-preview {
  font: var(--semantic-font-style-body-md);
  color: var(--semantic-color-text-secondary);
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
}

.delete-button {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: color 0.2s, background-color 0.2s;

  &:hover {
    color: var(--semantic-color-text-danger);
    background-color: var(--semantic-color-surface-danger-subtle);
  }

  .icon {
    width: 1rem;
    height: 1rem;
  }
}

.empty-state,
.empty-state-no-folder,
.loading-spinner {
  text-align: center;
  margin-top: 4rem;
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-body-lg);
  p + p {
    margin-top: 0.5rem;
    font: var(--semantic-font-style-body-md);
  }
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