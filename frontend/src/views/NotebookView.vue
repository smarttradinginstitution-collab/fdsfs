<template>
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
</template>

<script setup>
import { onMounted } from 'vue';
import { useNotebookStore } from '../stores/notebookStore';
import FolderList from '../components/notebook/FolderList.vue';
import NoteList from '../components/notebook/NoteList.vue';
import NoteEditor from '../components/notebook/NoteEditor.vue';

const store = useNotebookStore();

// Fetch the initial list of folders when the component is mounted
onMounted(() => {
  store.fetchFolders();
});
</script>

<style lang="scss" scoped>
.notebook-layout {
  display: grid;
  // Defines the three-column layout:
  // 1. Navigation Pane: fixed width
  // 2. Note List Pane: takes up 40% of the remaining space
  // 3. Editor Pane: takes up 60% of the remaining space
  grid-template-columns: 280px 0.6fr 1fr;
  height: calc(100vh - var(--header-height));
  background-color: var(--semantic-color-surface-primary);
  border-top: 1px solid var(--semantic-color-border-default);
}

.navigation-pane {
  border-right: 1px solid var(--semantic-color-border-default);
  overflow-y: auto;
  padding: 1rem;
}

.note-list-pane {
  border-right: 1px solid var(--semantic-color-border-default);
  overflow-y: auto;
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