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
          <button @click="toggleFolders" class="section-header">
            <ChevronDownIcon class="chevron-icon" :class="{ 'is-rotated': !foldersOpen }" />
            <span>Folders</span>
          </button>
          <ul v-show="foldersOpen" class="folder-list">
            <!-- System Folders -->
            <li v-if="store.isLoadingFolders">Loading...</li>
            <li
              v-for="folder in store.systemFolders"
              :key="folder.id"
              @click="selectFolder(folder.id)"
              class="folder-item is-system"
              :class="{ 'is-selected': store.selectedFolderId === folder.id }"
            >
              <div class="bookmark-tab" :style="{ backgroundColor: 'var(--semantic-color-text-secondary)' }"></div>
              <div class="folder-info">
                <span class="folder-name">{{ folder.name }}</span>
              </div>
              <span class="note-count-badge">{{ folder.note_count }}</span>
            </li>

            <!-- Separator -->
            <hr v-if="store.systemFolders.length > 0 && store.userFolders.length > 0" class="separator" />

            <!-- User Folders -->
            <li
              v-for="folder in store.userFolders"
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

        <!-- My Notes Section -->
        <div class="nav-section">
          <button @click="toggleMyNotes" class="section-header">
            <ChevronDownIcon class="chevron-icon" :class="{ 'is-rotated': !myNotesOpen }" />
            <span>My notes</span>
          </button>
          <div v-if="myNotesOpen" class="placeholder-content">
            <p>Notes content...</p>
          </div>
        </div>

        <!-- Tags Section -->
        <div class="nav-section">
          <button @click="toggleTags" class="section-header">
            <ChevronDownIcon class="chevron-icon" :class="{ 'is-rotated': !tagsOpen }" />
            <span>Tags</span>
          </button>
          <div v-if="tagsOpen" class="placeholder-content">
            <p>Tags content...</p>
          </div>
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
import { TrashIcon, FolderIcon, ChevronDownIcon } from '@heroicons/vue/24/outline';


const store = useNotebookStore();
const isAddFolderModalOpen = ref(false);
const foldersOpen = ref(true);
const myNotesOpen = ref(false);
const tagsOpen = ref(false);

const toggleFolders = () => {
  foldersOpen.value = !foldersOpen.value;
};

const toggleMyNotes = () => {
  myNotesOpen.value = !myNotesOpen.value;
};

const toggleTags = () => {
  tagsOpen.value = !tagsOpen.value;
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
  }
  :deep(.widget-header) {
    padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
    min-height: 50px;
  }
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.add-folder-button {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-inset-sm);
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;

  &:hover {
    color: var(--semantic-color-text-primary);
  }

  .icon {
    width: 1.125rem; // 18px
    height: 1.125rem;
  }
}

.folder-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  padding: var(--semantic-size-inset-md);
  padding-top: var(--semantic-size-inset-sm);
  gap: var(--semantic-size-inset-md);
}

.navigation {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-inset-lg);
  overflow-y: auto;
}

.nav-section {
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-inset-xs);
  width: 100%;
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--semantic-size-inset-sm);

  &:hover {
    color: var(--semantic-color-text-secondary);
  }
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
  gap: var(--semantic-size-inset-xs);
}

.separator {
  border: none;
  border-top: 1px solid var(--semantic-color-border-default);
  margin: var(--semantic-size-inset-sm) 0;
}

.placeholder-content {
  padding: var(--semantic-size-inset-xs) 0;
  padding-left: calc(1rem + var(--semantic-size-inset-xs)); // Align with folder text
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-disabled);
}

.folder-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  padding-left: calc(var(--semantic-size-inset-sm) + 6px); // Space for bookmark
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
  overflow: hidden;

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
  width: 4px; // Thinner bookmark
  border-right: 1px solid var(--semantic-color-border-default);
}

.folder-info {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-inset-sm);
}

.folder-name {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
}

.note-count-badge {
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-tertiary);
  padding: 2px var(--semantic-size-inset-xs);
  border-radius: var(--semantic-border-radius-pill);
}

.nav-item {
  font: var(--semantic-font-style-label-md);
  display: flex;
  align-items: center;
  gap: var(--semantic-size-inset-sm);
  padding: var(--semantic-size-inset-sm);
  color: var(--semantic-color-text-primary);
  text-decoration: none;
  border-radius: var(--semantic-border-radius-interactive);

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
  }

  .icon {
    width: 1.125rem; // 18px
    height: 1.125rem;
    color: var(--semantic-color-text-secondary);
  }
}

.footer {
  margin-top: auto;
  padding-top: var(--semantic-size-inset-md);
  border-top: 1px solid var(--semantic-color-border-default);
}
</style>