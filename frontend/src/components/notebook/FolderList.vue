<template>
  <BaseWidget class="folder-list-widget">
    <!-- Header: Add Folder -->
    <template #header>
      <div class="header-content">
        <button @click="isAddFolderModalOpen = true" class="add-folder-button">
          <FolderIcon class="icon" />
          <span>Add Folder</span>
        </button>
      </div>
    </template>

    <!-- Main Content: Folder List -->
    <div class="folder-list-container">
      <!-- Navigation -->
      <nav class="navigation">
        <!-- Folders Section -->
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
import '@vuepic/vue-datepicker/dist/main.css';
import { TrashIcon, FolderIcon } from '@heroicons/vue/24/outline';


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
  :deep(.widget-content) {
    padding: 0;
    display: flex;
  }
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.add-folder-button {
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

.folder-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  padding: 1rem;
  gap: 1rem;
}

.actions {
  display: none; // Hide old actions, log day is moved
}

.navigation {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
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
  gap: 0.5rem; // Space between folder items
}

.folder-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem 0.75rem 2rem; // Increased left padding for bookmark
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
  overflow: hidden; // Ensures bookmark is clipped by border-radius

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
  }

  &.is-selected {
    background-color: var(--semantic-color-surface-selected);
    .folder-name {
      color: var(--semantic-color-text-primary);
      font-weight: 600;
    }
  }
}

.bookmark-tab {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 8px;
  border-right: 1px solid var(--semantic-color-border-default);
}

.folder-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.folder-name {
  font: var(--semantic-font-style-label-lg);
  color: var(--semantic-color-text-secondary);
}

.note-count-badge {
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-tertiary);
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
  padding-top: 1rem;
  border-top: 1px solid var(--semantic-color-border-default);
}

.log-day-picker {
  display: none; // Hide the date picker, it's moved to NoteList
}
</style>