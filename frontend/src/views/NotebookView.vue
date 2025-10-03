<template>
  <div class="notebook-layout">
    <!-- Left Column: Folder List -->
    <div class="folder-list-pane">
      <FolderList />
    </div>

    <!-- Right Column: Note List or Note Editor -->
    <div class="main-pane">
      <NoteEditor v-if="store.selectedNote" />
      <NoteList v-else />
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

<style scoped>
.notebook-layout {
  display: grid;
  grid-template-columns: 300px 1fr; /* Fixed width for folder list, rest for main content */
  height: calc(100vh - var(--header-height, 60px)); /* Adjust based on your header's height */
  background-color: var(--semantic-color-surface-primary);
}

.folder-list-pane {
  border-right: 1px solid var(--semantic-color-border-default);
  overflow-y: auto;
}

.main-pane {
  overflow-y: auto;
}
</style>