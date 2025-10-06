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
  border-top: 1px solid var(--semantic-color-border-default);
}

.search-container {
  padding: var(--semantic-size-inset-md) var(--semantic-size-inset-md) 0;
  flex-shrink: 0;
}

.search-bar {
  position: relative;
  max-width: 400px;
  margin-bottom: var(--semantic-size-inset-md);
}

.search-input {
  font: var(--semantic-font-style-label-md);
  width: 100%;
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md) var(--semantic-size-inset-sm) 38px; // Custom left padding for icon
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
  left: var(--semantic-size-inset-md);
  top: 50%;
  transform: translateY(-50%);
  width: 1.125rem; // 18px
  height: 1.125rem; // 18px
  color: var(--semantic-color-text-secondary);
}

.notebook-layout {
  display: grid;
  grid-template-columns: 300px 260px 1fr; // Slightly more compact columns
  flex-grow: 1;
  gap: var(--semantic-size-inset-md);
  padding: 0 var(--semantic-size-inset-md) var(--semantic-size-inset-md);
  overflow: hidden;
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
  font: var(--semantic-font-style-body-lg);

  p + p {
    margin-top: var(--semantic-size-inset-xs);
    font: var(--semantic-font-style-body-md);
  }
}
</style>