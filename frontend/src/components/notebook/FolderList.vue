<template>
  <div class="folder-list-container">
    <header class="main-header">
      <h1 class="title">Notebook</h1>
    </header>

    <div class="actions-toolbar">
      <BaseButton
        variant="primary"
        class="add-folder-button"
        @click="isCreating = true"
      >
        <IconPlus />
        <span>Add folder</span>
      </BaseButton>
      <div class="search-wrapper">
        <IconSearch class="search-icon" />
        <input type="text" placeholder="Search notes..." class="search-input" />
      </div>
    </div>

    <!-- Create Folder Form -->
    <div v-if="isCreating" class="create-folder-form">
      <input
        v-model="newFolderName"
        @keyup.enter="handleCreateFolder"
        @keyup.esc="isCreating = false"
        placeholder="New folder name..."
        class="input-new-folder"
        ref="createInput"
      />
      <div class="form-actions">
        <BaseButton variant="primary" @click="handleCreateFolder">Save</BaseButton>
        <BaseButton variant="secondary" @click="isCreating = false">Cancel</BaseButton>
      </div>
    </div>

    <nav class="navigation-menu">
      <!-- Loading and Error States -->
      <div v-if="store.isLoadingFolders" class="loading-spinner">Loading...</div>
      <div v-else-if="store.error" class="error-message">{{ store.error }}</div>

      <!-- Folder List -->
      <ul v-else class="folders-list">
        <li class="nav-item">
          <IconBookOpen />
          <span>All notes</span>
        </li>
        <li class="nav-item">
          <IconTag />
          <span>Tags</span>
        </li>

        <!-- Accordion for Folders -->
        <li class="accordion">
          <div class="accordion-header" @click="toggleAccordion('folders')">
            <span>Folders</span>
            <IconChevronDown :class="{ 'is-rotated': accordions.folders }" />
          </div>
          <ul v-show="accordions.folders" class="accordion-content">
            <li
              v-for="folder in userFolders"
              :key="folder.id"
              @click="selectFolder(folder.id)"
              class="folder-item"
              :class="{ 'is-selected': store.selectedFolderId === folder.id }"
            >
              <span>{{ folder.name }}</span>
              <button @click.stop="handleDeleteFolder(folder.id)" class="delete-button">...</button>
            </li>
          </ul>
        </li>

        <!-- System Folders -->
        <li
            v-for="folder in systemFolders"
            :key="folder.id"
            @click="selectFolder(folder.id)"
            class="nav-item"
            :class="{ 'is-selected': store.selectedFolderId === folder.id }"
        >
            <IconJournal />
            <span>{{ folder.name }}</span>
            <span v-if="folder.notes.length > 0" class="badge">{{ folder.notes.length }}</span>
        </li>
      </ul>
    </nav>

    <footer class="sidebar-footer">
      <a href="#" @click.prevent="showDeleted" class="footer-link">
        <IconTrash />
        <span>Recently Deleted</span>
      </a>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, reactive } from 'vue';
import { useNotebookStore } from '../../stores/notebookStore';
import { FolderType } from '../../models/enums'; // Assuming enums are now in models
import BaseButton from '../ui/BaseButton.vue';
import IconPlus from '../icons/PlusIcon.vue';
import IconSearch from '../icons/IconSearch.vue';
import IconBookOpen from '../icons/BookOpenIcon.vue';
import IconTag from '../icons/IconTag.vue';
import IconChevronDown from '../icons/ChevronDownIcon.vue';
import IconJournal from '../icons/IconJournal.vue';
import IconTrash from '../icons/TrashIcon.vue';


const store = useNotebookStore();
const isCreating = ref(false);
const newFolderName = ref('');
const createInput = ref(null);

const accordions = reactive({
  folders: true, // Default to open
});

const userFolders = computed(() => store.folders.filter(f => f.folder_type === FolderType.USER));
const systemFolders = computed(() => store.folders.filter(f => f.folder_type === FolderType.SYSTEM));


watch(isCreating, (val) => {
  if (val) nextTick(() => createInput.value?.focus());
});

const handleCreateFolder = async () => {
  if (!newFolderName.value.trim()) return;
  await store.createFolder({ name: newFolderName.value });
  newFolderName.value = '';
  isCreating.value = false;
};

const handleDeleteFolder = async (folderId) => {
  if (confirm('Are you sure you want to delete this folder?')) {
    await store.deleteFolder(folderId);
  }
};

const selectFolder = (folderId) => {
  store.selectFolder(folderId);
};

const toggleAccordion = (name) => {
  accordions[name] = !accordions[name];
};

const showDeleted = () => {
  // This will be implemented later. It will fetch and show deleted items.
  console.log("Show recently deleted items");
  store.showDeleted(); // Placeholder for store action
};
</script>

<style lang="scss" scoped>
.folder-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-primary);
}

.main-header {
  padding-bottom: var(--fluid-spacing-m);
  .title {
    font-size: var(--fluid-font-size-xl);
    font-weight: 600;
  }
}

.actions-toolbar {
  display: flex;
  flex-direction: column;
  gap: var(--fluid-spacing-m);
  margin-bottom: var(--fluid-spacing-l);
}

.add-folder-button {
  width: 100%;
  justify-content: center;
  gap: var(--fluid-spacing-xs);
}

.search-wrapper {
  position: relative;
  .search-icon {
    position: absolute;
    left: var(--fluid-spacing-s);
    top: 50%;
    transform: translateY(-50%);
    color: var(--semantic-color-text-secondary);
  }
  .search-input {
    width: 100%;
    padding: var(--fluid-spacing-s) var(--fluid-spacing-s) var(--fluid-spacing-s) var(--fluid-spacing-xl);
    background-color: var(--semantic-color-surface-secondary);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-interactive);
    color: var(--semantic-color-text-primary);
    font-size: var(--fluid-font-size-m);
    &:focus {
      outline: none;
      border-color: var(--semantic-color-border-focus);
    }
  }
}

.navigation-menu {
  flex-grow: 1;
  overflow-y: auto;
}

.folders-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item, .accordion-header, .folder-item {
  display: flex;
  align-items: center;
  gap: var(--fluid-spacing-m);
  padding: var(--fluid-spacing-s) var(--fluid-spacing-xs);
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: var(--semantic-color-surface-secondary-hover);
  }

  &.is-selected {
    background-color: var(--semantic-color-interactive-primary-default);
    color: var(--semantic-color-text-on-primary);
  }
}

.accordion-header {
  justify-content: space-between;
  font-weight: 600;
}

.accordion-content {
  list-style: none;
  padding-left: var(--fluid-spacing-l);
}

.folder-item {
  justify-content: space-between;
  .delete-button {
    background: none;
    border: none;
    color: var(--semantic-color-text-secondary);
    visibility: hidden;
    opacity: 0;
    &:hover {
      color: var(--semantic-color-text-danger);
    }
  }
  &:hover .delete-button {
    visibility: visible;
    opacity: 1;
  }
}

.badge {
  margin-left: auto;
  font-size: var(--fluid-font-size-xs);
  padding: 2px 6px;
  border-radius: 8px;
  background-color: var(--semantic-color-surface-tertiary);
}

.is-selected .badge {
    background-color: var(--semantic-color-surface-primary);
    color: var(--semantic-color-text-primary);
}

.sidebar-footer {
  padding-top: var(--fluid-spacing-m);
  border-top: 1px solid var(--semantic-color-border-default);
}

.footer-link {
  display: flex;
  align-items: center;
  gap: var(--fluid-spacing-m);
  padding: var(--fluid-spacing-s);
  text-decoration: none;
  color: var(--semantic-color-text-secondary);
  border-radius: var(--semantic-border-radius-interactive);

  &:hover {
    background-color: var(--semantic-color-surface-secondary-hover);
    color: var(--semantic-color-text-primary);
  }
}
</style>