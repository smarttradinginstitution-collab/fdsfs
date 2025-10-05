<template>
  <div class="page-container">
    <!-- Search Bar -->
    <div class="search-container">
      <div class="search-bar">
        <MagnifyingGlassIcon class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search notes..."
          class="search-input"
        />
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="notebook-layout">
      <!-- Column 1: Folder List -->
      <div class="grid-pane">
        <FolderList />
      </div>

      <!-- Column 2: Note List -->
      <div class="grid-pane">
        <NoteList :search-query="searchQuery" />
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
import { ref, onMounted } from 'vue';
import { useNotebookStore } from '../stores/notebookStore';
import FolderList from '../components/notebook/FolderList.vue';
import NoteList from '../components/notebook/NoteList.vue';
import NoteEditor from '../components/notebook/NoteEditor.vue';
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline';

const store = useNotebookStore();
const searchQuery = ref('');

// Fetch the initial list of folders when the component is mounted
onMounted(() => {
  store.fetchFolders();
});
</script>

<style lang="scss" scoped>
.page-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - var(--header-height));
  background-color: var(--semantic-color-surface-primary);
  border-top: 1px solid var(--semantic-color-border-default);
}

.search-container {
  padding: 1rem 1rem 0 1rem;
  flex-shrink: 0;
}

.search-bar {
  position: relative;
  max-width: 400px; // Or any width you prefer
  margin-bottom: 1rem;
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
  // Adjusted column widths: Folder list is wider, note list is narrower.
  grid-template-columns: 320px 280px 1fr;
  flex-grow: 1;
  gap: 1rem;
  padding: 0 1rem 1rem 1rem;
  overflow: hidden; // Prevents double scrollbars
}

.grid-pane {
  overflow-y: auto;
  height: 100%;
}

.editor-pane {
  overflow-y: auto;
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