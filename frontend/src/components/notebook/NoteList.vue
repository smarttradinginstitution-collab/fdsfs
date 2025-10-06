<template>
  <BaseWidget class="note-list-widget">
    <!-- Header: Conditional Buttons -->
    <template #header>
      <div class="header-content">
        <!-- "New Note" for Trade Notes folder -->
        <button v-if="headerType === 'new_note'" @click="isTradeNoteModalOpen = true" class="action-button">
          <PencilSquareIcon class="icon" />
          <span>New Note</span>
        </button>

        <!-- "Log Day" for Daily Journal and User folders -->
        <VueDatePicker
          v-if="headerType === 'log_day'"
          v-model="logDayDate"
          @update:model-value="handleLogDay"
          :enable-time-picker="false"
          auto-apply
          dark
          :teleport="true"
        >
          <template #trigger>
            <button class="action-button">
              <CalendarDaysIcon class="icon" />
              <span>Log Day</span>
            </button>
          </template>
        </VueDatePicker>

        <!-- "Log Session" for Session Recap folder -->
        <VueDatePicker
          v-if="headerType === 'session_recap'"
          v-model="sessionDateRange"
          @update:model-value="handleLogSession"
          range
          :enable-time-picker="false"
          auto-apply
          dark
          :teleport="true"
        >
          <template #trigger>
            <button class="action-button">
              <CalendarDaysIcon class="icon" />
              <span>Log Session</span>
            </button>
          </template>
        </VueDatePicker>
        <!-- No header for "All Notes" -->
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
        </div>
      </div>
      <div v-else class="empty-state-no-folder">
        <p>Select a folder to see your notes.</p>
      </div>
    </div>

    <!-- Modals -->
    <TradeNoteModal
      :is-open="isTradeNoteModalOpen"
      @close="isTradeNoteModalOpen = false"
      @create="handleCreateTradeNote"
    />
  </BaseWidget>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import BaseWidget from '../layout/BaseWidget.vue';
import VueDatePicker from '@vuepic/vue-datepicker';
import TradeNoteModal from './TradeNoteModal.vue';
import '@vuepic/vue-datepicker/dist/main.css';
import { TrashIcon, CalendarDaysIcon, PencilSquareIcon } from '@heroicons/vue/24/outline';

const props = defineProps({
  searchQuery: {
    type: String,
    default: '',
  },
});

const store = useNotebookStore();
const logDayDate = ref(null);
const sessionDateRange = ref(null);
const isTradeNoteModalOpen = ref(false);

const headerType = computed(() => {
  const folderName = store.selectedFolder?.name;
  if (!folderName || folderName === 'All Notes') return 'none';
  if (folderName === 'Trade Notes') return 'new_note';
  if (folderName === 'Session Recap') return 'session_recap';
  return 'log_day'; // Default for Daily Journal and user folders
});

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
    alert('Please select a folder before logging a day.');
    return;
  }
  try {
    await store.logDay(date);
    logDayDate.value = null;
  } catch (error) {
    console.error('Error logging day from component:', error);
  }
};

const handleCreateTradeNote = async (noteData) => {
  if (!store.selectedFolderId) return;
  try {
    await store.createNote({
      ...noteData,
      folder_id: store.selectedFolderId,
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
    });
    isTradeNoteModalOpen.value = false;
  } catch (error) {
    console.error('Failed to create trade note:', error);
  }
};

const handleLogSession = async (dateRange) => {
  if (!dateRange || dateRange.length < 2 || !store.selectedFolderId) {
    alert('Please select a date range for the session recap.');
    return;
  }
  const [startDate, endDate] = dateRange;
  try {
    await store.logSession(startDate, endDate);
    sessionDateRange.value = null;
  } catch (error) {
    console.error('Error logging session from component:', error);
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
  :deep(.widget-header) {
    padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
    min-height: 50px;
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
  gap: var(--semantic-size-inset-sm);
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;

  &:hover {
    color: var(--semantic-color-text-primary);
  }

  .icon {
    width: 1.125rem; // 18px
    height: 1.125rem;
  }
}

.note-list-container {
  padding: var(--semantic-size-inset-md);
  height: 100%;
  width: 100%;
}

.notes {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-inset-sm);
}

.note-item {
  padding: var(--semantic-size-inset-md);
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
  font: var(--semantic-font-style-heading-sm);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-inset-xs);
}

.note-preview {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  margin-bottom: var(--semantic-size-inset-sm);
  line-height: 1.4;
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
  padding: 2px;
  border-radius: 50%;
  transition: color 0.2s, background-color 0.2s;

  &:hover {
    color: var(--semantic-color-text-danger);
    background-color: var(--semantic-color-surface-danger-subtle);
  }

  .icon {
    width: 0.875rem; // 14px
    height: 0.875rem;
  }
}

.empty-state,
.empty-state-no-folder,
.loading-spinner {
  text-align: center;
  margin-top: var(--semantic-size-inset-xl);
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-body-lg);
  p + p {
    margin-top: var(--semantic-size-inset-xs);
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