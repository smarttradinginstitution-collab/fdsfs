<template>
  <div class="note-list-container">
    <header class="list-header">
      <BaseButton variant="secondary" @click="logDay">
        <IconCalendar />
        Log day
      </BaseButton>
      <div class="header-actions">
        <label class="select-all-label">
          <input type="checkbox" v-model="selectAll" />
          Select All
        </label>
        <button class="icon-button" aria-label="Collapse panel">
          <IconChevronLeft />
        </button>
      </div>
    </header>

    <div v-if="store.isLoadingNotes" class="loading-spinner">Loading notes...</div>
    <div v-else-if="store.error" class="error-message">{{ store.error }}</div>

    <ul v-else-if="store.notes.length > 0" class="notes-list">
      <li
        v-for="note in store.notes"
        :key="note.id"
        @click="selectNote(note.id)"
        class="note-card"
        :class="{ 'is-selected': store.selectedNoteId === note.id }"
      >
        <h3 class="note-title">{{ formatDate(note.created_at, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }) }}</h3>
        <p class="note-subtitle">{{ formatDate(note.created_at) }}</p>
      </li>
    </ul>

    <div v-else class="empty-state">
      <IconJournal class="empty-icon" />
      <h4>No notes yet</h4>
      <p>Select a folder and click "Log day" to start.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useNotebookStore } from '@/stores/notebookStore';
import BaseButton from '@/components/ui/BaseButton.vue';
import IconCalendar from '@/components/icons/CalendarIcon.vue';
import IconChevronLeft from '@/components/icons/ArrowLeftIcon.vue';
import IconJournal from '@/components/icons/IconJournal.vue';

const store = useNotebookStore();
const selectAll = ref(false);

const selectNote = (noteId) => {
  store.selectNote(noteId);
};

const logDay = () => {
  if (!store.selectedFolderId) {
    alert("Please select a folder first.");
    return;
  }

  const today = new Date();
  const title = `Log - ${today.toLocaleDateString('en-CA')}`; // YYYY-MM-DD

  const templateContent = store.selectedFolder?.template_content;
  const noteContent = templateContent || { type: 'doc', content: [{ type: 'paragraph' }] };

  store.createNote({
    folder_id: store.selectedFolderId,
    title: title,
    content: noteContent
  });
};

const formatDate = (dateString, options = {}) => {
  const date = new Date(dateString);
  const defaultOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  };
  return date.toLocaleDateString(undefined, { ...defaultOptions, ...options });
};
</script>

<style lang="scss" scoped>
.note-list-container {
  padding: var(--fluid-spacing-m);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--fluid-spacing-m);
  flex-shrink: 0;

  .base-button {
    gap: var(--fluid-spacing-xs);
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--fluid-spacing-m);
}

.select-all-label {
  display: flex;
  align-items: center;
  gap: var(--fluid-spacing-xs);
  font-size: var(--fluid-font-size-m);
  cursor: pointer;
}

.icon-button {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  padding: var(--fluid-spacing-xs);
  border-radius: var(--semantic-border-radius-interactive);
  &:hover {
    background-color: var(--semantic-color-surface-tertiary);
  }
}

.notes-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex-grow: 1;
}

.note-card {
  padding: var(--fluid-spacing-m);
  border-radius: var(--semantic-border-radius-container);
  margin-bottom: var(--fluid-spacing-s);
  cursor: pointer;
  transition: background-color 0.2s ease;
  border: 1px solid transparent;

  &:hover {
    background-color: var(--semantic-color-surface-tertiary);
  }

  &.is-selected {
    background-color: var(--semantic-color-surface-elevated-primary);
    border-color: var(--semantic-color-border-focus);
  }
}

.note-title {
  font-size: var(--fluid-font-size-m);
  font-weight: 600;
  color: var(--semantic-color-text-primary);
  margin: 0 0 var(--fluid-spacing-xxs) 0;
}

.note-subtitle {
  font-size: var(--fluid-font-size-s);
  color: var(--semantic-color-text-secondary);
  margin: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: var(--semantic-color-text-secondary);
  height: 100%;

  .empty-icon {
    width: 48px;
    height: 48px;
    margin-bottom: var(--fluid-spacing-m);
    color: var(--semantic-color-text-disabled);
  }

  h4 {
    font-size: var(--fluid-font-size-l);
    font-weight: 600;
    color: var(--semantic-color-text-primary);
    margin: 0 0 var(--fluid-spacing-xs) 0;
  }
}
</style>