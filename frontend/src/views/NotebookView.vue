<template>
  <div class="notebook-layout">
    <!-- Column 1: Folder List -->
    <div class="folder-list-pane">
      <FolderList />
    </div>

    <!-- Column 2: Note List -->
    <div class="note-list-pane">
      <NoteList />
    </div>

    <!-- Column 3: Note Editor -->
    <div class="main-pane">
      <NoteEditor v-if="store.selectedNote" :key="store.selectedNote.id" />
      <div v-else class="empty-editor-state">
        <p>Select a note to view or edit.</p>
        <p class="text-sm text-gray-500">Or create a new one in the desired folder.</p>
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
  // A responsive 3-column layout. The first two have a max-width and the last one takes the remaining space.
  grid-template-columns: minmax(280px, 1fr) minmax(320px, 1.2fr) 3fr;
  height: calc(100vh - var(--header-height)); // Assuming --header-height is globally available
  background-color: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-primary);
}

.folder-list-pane {
  border-right: 1px solid var(--semantic-color-border-default);
  overflow-y: auto;
  padding: var(--fluid-spacing-m);
}

.note-list-pane {
  border-right: 1px solid var(--semantic-color-border-default);
  overflow-y: auto;
  background-color: var(--semantic-color-surface-secondary);
}

.main-pane {
  overflow-y: auto;
  padding: var(--fluid-spacing-l);
}

.empty-editor-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--semantic-color-text-secondary);
  text-align: center;
  font-size: var(--fluid-font-size-l);

  p {
    margin: 0;
  }

  .text-sm {
    margin-top: var(--fluid-spacing-xs);
    font-size: var(--fluid-font-size-s);
  }
}

// Responsive adjustments
@include media-down(lg) {
  .notebook-layout {
    grid-template-columns: 280px 1fr;
    .main-pane {
      // On medium screens, maybe hide the editor if no note is selected
      // This is a placeholder for a more defined responsive behavior
      display: block;
    }
  }
}

@include media-down(md) {
  .notebook-layout {
    // Stack columns on mobile
    grid-template-columns: 1fr;

    // Example of how to handle column visibility on mobile
    // This would need a bit of state logic to work correctly
    .note-list-pane, .main-pane {
       display: none; // Simplified for now
    }
  }
}
</style>