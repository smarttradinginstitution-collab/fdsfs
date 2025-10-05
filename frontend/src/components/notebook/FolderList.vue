<template>
  <BaseWidget class="folder-list-widget">
    <!-- Header: "Add Folder" action -->
    <template #header>
      <div class="header-content">
        <button @click="isAddFolderModalOpen = true" class="add-folder-button">
          <FolderIcon class="icon" />
          <span>Add Folder</span>
        </button>
      </div>
    </template>

    <!-- Main Content: Navigation and Folder List -->
    <div class="folder-list-container">
      <nav class="navigation">
        <!-- Folders Section (Collapsible) -->
        <div class="nav-section">
          <button @click="toggleFolders" class="section-header">
            <ChevronDownIcon class="chevron-icon" :class="{ 'is-rotated': !foldersOpen }" />
            <span>Folders</span>
          </button>
          <ul v-show="foldersOpen" class="folder-list">
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
import { TrashIcon, FolderIcon, ChevronDownIcon } from '@heroicons/vue/24/outline';

const store = useNotebookStore();
const isAddFolderModalOpen = ref(false);
const foldersOpen = ref(true);

const toggleFolders = () => {
  foldersOpen.value = !foldersOpen.value;
};

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
    flex-direction: column;
    overflow-y: auto;
  }
}

.header-content {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 100%;
}

.add-folder-button {
  font: var(--semantic-font-style-label-md-bold);
  color: var(--semantic-color-text-interactive);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--semantic-size-stack-xxs);
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-xs);

  &:hover {
    text-decoration: underline;
  }

  .icon {
    width: 1.25rem;
    height: 1.25rem;
  }
}

.folder-list-container {
  display: flex;
  flex-direction: column;
  padding: var(--semantic-size-inset-md);
  gap: var(--semantic-size-stack-sm);
}

.navigation {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.nav-section {
  display: flex;
  flex-direction: column;
}

.section-header {
  font: var(--semantic-font-style-label-sm);
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-xs);
  color: var(--semantic-color-text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--semantic-size-stack-xxs) 0;
  margin-bottom: var(--semantic-size-stack-xs);
}

.chevron-icon {
  width: 1rem;
  height: 1rem;
  transition: transform 0.2s ease-in-out;
  &.is-rotated {
    transform: rotate(-90deg);
  }
}

.folder-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
}

.folder-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-sm) var(--semantic-size-inset-sm) var(--semantic-size-inset-lg);
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
  width: var(--semantic-size-component-notebook-bookmark-width);
  height: 60%;
  background-color: var(--semantic-color-border-default);
  border-top-right-radius: 2px;
  border-bottom-right-radius: 2px;
}

.folder-info {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-inset-sm);
}

.folder-name {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);
}

.note-count-badge {
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-secondary);
  padding: var(--semantic-size-inset-xxs) var(--semantic-size-inset-xs);
  border-radius: var(--semantic-border-radius-pill);
}

.nav-item {
  font: var(--semantic-font-style-label-md);
  display: flex;
  align-items: center;
  gap: var(--semantic-size-inset-sm);
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
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