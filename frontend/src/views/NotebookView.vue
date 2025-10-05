<template>
  <div class="notebook-view-container">
    <!-- Top Search Bar -->
    <div class="search-bar-container">
      <div class="search-bar">
        <MagnifyingGlassIcon class="search-icon" />
        <input
          type="text"
          placeholder="Search notes..."
          class="search-input"
          :value="store.searchQuery"
          @input="store.setSearchQuery($event.target.value)"
        />
      </div>
    </div>

    <!-- Main Content Layout -->
    <div class="notebook-layout">
      <!-- Column 1: Folder List & Navigation -->
      <div class="navigation-pane">
        <FolderList />
      </div>

      <!-- Column 2: Note List -->
      <div class="note-list-pane">
        <NoteList />
      </div>

      <!-- Column 3: Note Editor -->
      <div class="editor-pane">
        <NoteEditor v-if="store.selectedNote" />
        <div v-else class="editor-placeholder">
          <p>Select a note to view or edit it.</p>
          <p>Or, select a folder and create a new note.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useNotebookStore } from '../stores/notebookStore';
import FolderList from '../components/notebook/FolderList.vue';
import NoteList from '../components/notebook/NoteList.vue';
import NoteEditor from '../components/notebook/NoteEditor.vue';
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline';

const store = useNotebookStore();

// Fetch the initial list of folders when the component is mounted
onMounted(() => {
  store.fetchFolders();
});
</script>

<style lang="scss" scoped>
.notebook-view-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - var(--header-height));
  background-color: var(--semantic-color-surface-primary);
  border-top: 1px solid var(--semantic-color-border-default);
}

.search-bar-container {
  padding: var(--semantic-size-inset-md) var(--semantic-size-inset-md) 0 var(--semantic-size-inset-md);
  /* Borders removed to let cards define the layout */
}

.search-bar {
  position: relative;
  max-width: 500px;
}

.search-input {
  font: var(--semantic-font-style-label-md);
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.25rem;
  background-color: var(--semantic-color-surface-secondary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  color: var(--semantic-color-text-primary);
  &:focus {
    outline: none;
    border-color: var(--semantic-color-border-focus);
  }
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.25rem;
  height: 1.25rem;
  color: var(--semantic-color-text-secondary);
}

.notebook-layout {
  display: grid;
  /* Use the new token for column width */
  grid-template-columns: var(--semantic-size-component-notebook-column-width) var(--semantic-size-component-notebook-column-width) 1fr;
  flex-grow: 1;
  /* overflow: hidden; // This was preventing the grid from expanding correctly */
  gap: var(--semantic-size-stack-sm); /* Use stack token for gap */
  padding: var(--semantic-size-inset-md); /* Use inset token for padding */
}

.navigation-pane,
.note-list-pane,
.editor-pane {
  /* overflow-y is now handled by the BaseWidget component */
  min-height: 0; /* Prevent grid items from growing beyond their container */
}

/* Panes no longer need individual padding or borders */
.navigation-pane {
  padding: 0;
}

.note-list-pane {
  padding: 0;
}

.editor-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--semantic-color-text-secondary);
  text-align: center;
}
</style>