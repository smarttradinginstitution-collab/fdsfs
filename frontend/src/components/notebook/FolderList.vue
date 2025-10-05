<template>
  <BaseWidget class="folder-list-widget">
    <!-- Header: Title and "Add Folder" action -->
    <template #header>
      <div class="header-content">
        <h2 class="title">Folders</h2>
        <button @click="isAddFolderModalOpen = true" class="add-folder-button">
          + Add Folder
        </button>
      </div>
    </template>

    <!-- Main Content: Navigation and Folder List -->
    <div class="folder-list-container">
      <nav class="navigation">
        <!-- Folders Section (Collapsible) -->
        <div class="nav-section">
          <ul class="folder-list">
            <li v-if="store.isLoadingFolders">Loading...</li>
            <li
              v-for="folder in store.folders"
              :key="folder.id"
              @click="selectFolder(folder.id)"
              class="folder-item"
              :class="{ 'is-selected': store.selectedFolderId === folder.id }"
            >
              <div class="bookmark-tab" :style="{ backgroundColor: folder.color }"></div>
              <div class="folder-info">
                <span class="folder-name">{{ folder.name }}</span>
              </div>
              <span class="note-count-badge">{{ folder.note_count }}</span>
            </li>
          </ul>
        </div>

        <!-- Other Links -->
        <div class="nav-section">
          <a href="#" class="nav-item">My notes</a>
          <a href="#" class="nav-item">Tags</a>
        </div>
      </nav>

      <!-- Footer -->
      <div class="footer">
        <a href="#" class="nav-item">
          <TrashIcon class="icon" />
          Recently Deleted
        </a>
      </div>
    </div>

    <!-- Add Folder Modal -->
    <AddFolderModal
      :is-open="isAddFolderModalOpen"
      @close="isAddFolderModalOpen = false"
      @create="handleCreateFolder"
    />
  </BaseWidget>
</template>

<script setup>
import { ref } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import BaseWidget from '../layout/BaseWidget.vue';
import AddFolderModal from './AddFolderModal.vue';
import { TrashIcon } from '@heroicons/vue/24/outline';

const store = useNotebookStore();
const isAddFolderModalOpen = ref(false);

const selectFolder = (folderId) => {
  store.selectFolder(folderId);
};

const handleCreateFolder = async (folderData) => {
  try {
    await store.createFolder(folderData);
    isAddFolderModalOpen.value = false;
  } catch (error) {
    console.error('Failed to create folder from component:', error);
  }
};
</script>

<style lang="scss" scoped>
.folder-list-widget {
  // The BaseWidget provides the card structure, so we just need to ensure
  // its content is laid out correctly.
  :deep(.widget-content) {
    padding: 0;
    display: flex;
    flex-direction: column;
  }
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.title {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
}

.add-folder-button {
  font: var(--semantic-font-style-label-md-bold);
  color: var(--semantic-color-text-interactive);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  &:hover {
    text-decoration: underline;
  }
}

.folder-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
  gap: 1rem;
  overflow-y: auto;
}

.navigation {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.nav-section {
  display: flex;
  flex-direction: column;
}

.folder-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem; /* Increased gap for better spacing with bookmarks */
}

.folder-item {
  position: relative; /* For positioning the bookmark */
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0.75rem 0.6rem 1.5rem; /* Add left padding for bookmark */
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
  }

  &.is-selected {
    background-color: var(--semantic-color-surface-selected);
  }
}

.bookmark-tab {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background-color: var(--semantic-color-border-default); /* Fallback color */
  border-top-right-radius: 2px;
  border-bottom-right-radius: 2px;
}

.folder-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.folder-name {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);
}

.note-count-badge {
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-secondary);
  padding: 0.125rem 0.5rem;
  border-radius: var(--semantic-border-radius-pill);
}

.nav-item {
  font: var(--semantic-font-style-label-md);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  color: var(--semantic-color-text-primary);
  text-decoration: none;
  border-radius: var(--semantic-border-radius-interactive);

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
  }

  .icon {
    width: 1.25rem;
    height: 1.25rem;
    color: var(--semantic-color-text-secondary);
  }
}

.footer {
  margin-top: auto;
}
</style>