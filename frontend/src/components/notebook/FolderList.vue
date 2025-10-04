<template>
  <div class="folder-list-container">
    <div class="header">
      <h1 class="title">Notebook</h1>
    </div>

    <!-- Actions -->
    <div class="actions">
      <BaseButton class="action-button" variant="primary" @click="isAddFolderModalOpen = true">
        <PlusIcon class="icon" />
        Add folder
      </BaseButton>
      <VueDatePicker
        v-model="logDayDate"
        @update:model-value="handleLogDay"
        :enable-time-picker="false"
        auto-apply
        dark
        :teleport="true"
        placeholder="Log Day"
        class="log-day-picker"
      >
        <template #trigger>
          <BaseButton class="action-button" variant="secondary">
            <CalendarIcon class="icon" />
            Log day
          </BaseButton>
        </template>
      </VueDatePicker>
    </div>

    <!-- Search -->
    <div class="search-bar">
      <MagnifyingGlassIcon class="search-icon" />
      <input type="text" placeholder="Search notes..." class="search-input" />
    </div>

    <!-- Navigation -->
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
            <div class="folder-info">
              <span class="folder-color-dot" :style="{ backgroundColor: folder.color }"></span>
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

    <!-- Add Folder Modal -->
    <AddFolderModal
      :is-open="isAddFolderModalOpen"
      @close="isAddFolderModalOpen = false"
      @create="handleCreateFolder"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import BaseButton from '../ui/BaseButton.vue';
import AddFolderModal from './AddFolderModal.vue';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { PlusIcon, CalendarIcon, MagnifyingGlassIcon, ChevronDownIcon, TrashIcon } from '@heroicons/vue/24/outline';

const store = useNotebookStore();
const foldersOpen = ref(true);
const isAddFolderModalOpen = ref(false);
const logDayDate = ref(null);

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

const handleLogDay = async (date) => {
  if (!date) return;
  try {
    await store.logDay(date);
  } catch (error) {
    console.error("Error logging day from component:", error);
  } finally {
    logDayDate.value = null;
  }
};
</script>

<style lang="scss" scoped>
.folder-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

.header .title {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  flex-grow: 1;
  .icon {
    width: 1rem;
    height: 1rem;
  }
}

.search-bar {
  position: relative;
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

.section-header {
  font: var(--semantic-font-style-label-sm);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--semantic-color-text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem 0;
  margin-bottom: 0.5rem;
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
  gap: 0.25rem;
}

.folder-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
  }

  &.is-selected {
    background-color: var(--semantic-color-surface-selected);
    color: var(--semantic-color-text-primary);
  }
}

.folder-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.folder-color-dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  border: 1px solid var(--semantic-color-border-default);
}

.folder-name {
  font: var(--semantic-font-style-label-md);
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

.log-day-picker {
  flex-grow: 1;

  :global(.dp__theme_dark) {
    --dp-background-color: var(--semantic-color-surface-secondary);
    --dp-text-color: var(--semantic-color-text-primary);
    --dp-hover-color: var(--semantic-color-surface-tertiary);
    --dp-hover-text-color: var(--semantic-color-text-primary);
    --dp-primary-color: var(--semantic-color-interactive-primary-default);
    --dp-primary-text-color: var(--semantic-color-text-on-primary);
    --dp-border-color: var(--semantic-color-border-default);
    --dp-border-color-hover: var(--semantic-color-border-focus);
    --dp-icon-color: var(--semantic-color-text-secondary);
  }
}
</style>