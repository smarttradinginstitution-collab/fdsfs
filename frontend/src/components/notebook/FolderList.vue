<template>
  <div class="folder-list-container">
    <header class="main-header">
      <h1 class="title">Notebook</h1>
    </header>

    <div class="search-wrapper">
      <IconSearch class="search-icon" />
      <input type="text" placeholder="Search notes..." class="search-input" />
    </div>

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
      <ul class="nav-list">
        <li class="nav-item" @click="isCreating = true">
          <IconFolderPlus class="nav-icon" />
          <span>Add folder</span>
        </li>
        <li class="nav-item" @click="logDay">
          <IconCalendar class="nav-icon" />
          <span>Log day</span>
        </li>
      </ul>

      <ul class="nav-list accordions">
        <li class="accordion">
          <div class="accordion-header" @click="toggleAccordion('folders')">
            <div class="header-content">
              <IconFolder class="nav-icon" />
              <span>Folders</span>
            </div>
            <IconChevronDown class="chevron-icon" :class="{ 'is-rotated': accordions.folders }" />
          </div>
          <ul v-show="accordions.folders" class="accordion-content">
            <li v-for="folder in systemFolders" :key="folder.id" @click="selectFolder(folder.id)" class="folder-item">
              <span>{{ folder.name }}</span>
            </li>
          </ul>
        </li>

        <li class="section-header">My notes</li>
        <ul class="accordion-content" style="display: block;">
          <li v-for="folder in userFolders" :key="folder.id" @click="selectFolder(folder.id)" class="folder-item" :class="{ 'is-selected': store.selectedFolderId === folder.id }">
            <span>{{ folder.name }}</span>
            <span v-if="folder.notes.length > 0" class="badge">{{ folder.notes.length }}</span>
          </li>
        </ul>

        <li class="accordion">
           <div class="accordion-header" @click="toggleAccordion('tags')">
            <div class="header-content">
              <IconTag class="nav-icon" />
              <span>Tags</span>
            </div>
            <IconChevronDown class="chevron-icon" :class="{ 'is-rotated': !accordions.tags }" />
          </div>
          <!-- Tags content would go here -->
        </li>
      </ul>
    </nav>

    <footer class="sidebar-footer">
      <a href="#" @click.prevent="showDeleted" class="footer-link">
        <IconTrash class="nav-icon" />
        <span>Recently Deleted</span>
      </a>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, reactive } from 'vue';
import { useNotebookStore } from '@/stores/notebookStore';
import { FolderType } from '@/models/enums';
import BaseButton from '@/components/ui/BaseButton.vue';
import IconFolderPlus from '@/components/icons/IconFolderPlus.vue';
import IconCalendar from '@/components/icons/CalendarIcon.vue';
import IconSearch from '@/components/icons/IconSearch.vue';
import IconFolder from '@/components/icons/IconFolder.vue';
import IconTag from '@/components/icons/IconTag.vue';
import IconChevronDown from '@/components/icons/ChevronDownIcon.vue';
import IconTrash from '@/components/icons/TrashIcon.vue';


const store = useNotebookStore();
const isCreating = ref(false);
const newFolderName = ref('');
const createInput = ref(null);

const accordions = reactive({
  folders: true,
  tags: false,
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

const selectFolder = (folderId) => {
  store.selectFolder(folderId);
};

const toggleAccordion = (name) => {
  accordions[name] = !accordions[name];
};

const logDay = () => {
  console.log("This should probably create a new note in a 'Daily Log' folder");
};

const showDeleted = () => {
  store.showDeleted(); // Placeholder for store action
};
</script>

<style lang="scss" scoped>
.folder-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--fluid-spacing-m);
  gap: var(--fluid-spacing-m);
}

.main-header .title {
  font-size: var(--fluid-font-size-xl);
  font-weight: 600;
}

.search-wrapper {
  position: relative;
  .search-icon {
    position: absolute;
    left: var(--fluid-spacing-s);
    top: 50%;
    transform: translateY(-50%);
    color: var(--semantic-color-text-secondary);
    width: 18px; height: 18px;
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
  display: flex;
  flex-direction: column;
  gap: var(--fluid-spacing-l);
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--fluid-spacing-xs);
}

.nav-item, .accordion-header {
  display: flex;
  align-items: center;
  gap: var(--fluid-spacing-s);
  padding: var(--fluid-spacing-s);
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-weight: 500;

  &:hover {
    background-color: var(--semantic-color-surface-secondary-hover);
  }

  .nav-icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    color: var(--semantic-color-text-secondary);
  }
}

.accordion-header {
  justify-content: space-between;
  .header-content {
    display: flex;
    align-items: center;
    gap: var(--fluid-spacing-s);
  }
  .chevron-icon {
    width: 16px;
    height: 16px;
    transition: transform 0.2s ease-in-out;
    &.is-rotated {
      transform: rotate(180deg);
    }
  }
}

.accordion-content {
  list-style: none;
  padding-left: var(--fluid-spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--fluid-spacing-xxs);
  margin-top: var(--fluid-spacing-xs);
}

.folder-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--fluid-spacing-s);
  border-radius: var(--semantic-border-radius-interactive);
  cursor: pointer;
  font-size: var(--fluid-font-size-m);
  color: var(--semantic-color-text-secondary);
  font-weight: 400;

  &:hover {
    background-color: var(--semantic-color-surface-secondary-hover);
    color: var(--semantic-color-text-primary);
  }
  &.is-selected {
    background-color: var(--semantic-color-interactive-primary-default);
    color: var(--semantic-color-text-on-primary);
    font-weight: 500;
  }
}

.section-header {
  font-size: var(--fluid-font-size-s);
  font-weight: 600;
  color: var(--semantic-color-text-secondary);
  padding: var(--fluid-spacing-m) var(--fluid-spacing-s) var(--fluid-spacing-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge {
  font-size: var(--fluid-font-size-xs);
  padding: 2px 6px;
  border-radius: var(--semantic-border-radius-full);
  background-color: var(--semantic-color-surface-tertiary);
  color: var(--semantic-color-text-secondary);
}
.folder-item.is-selected .badge {
  background-color: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-primary);
}

.sidebar-footer {
  padding-top: var(--fluid-spacing-m);
  border-top: 1px solid var(--semantic-color-border-default);

  .footer-link {
    display: flex;
    align-items: center;
    gap: var(--fluid-spacing-s);
    padding: var(--fluid-spacing-s);
    text-decoration: none;
    color: var(--semantic-color-text-secondary);
    border-radius: var(--semantic-border-radius-interactive);

    &:hover {
      background-color: var(--semantic-color-surface-secondary-hover);
      color: var(--semantic-color-text-primary);
    }
  }
}

.create-folder-form {
  margin-top: var(--fluid-spacing-m);
  .input-new-folder {
    width: 100%;
    padding: var(--fluid-spacing-s);
    margin-bottom: var(--fluid-spacing-s);
    background-color: var(--semantic-color-surface-secondary);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-interactive);
    color: var(--semantic-color-text-primary);
  }
  .form-actions {
    display: flex;
    gap: var(--fluid-spacing-s);
  }
}
</style>