<template>
  <div v-if="note" class="note-editor-container">
    <!-- Editor Header -->
    <header class="editor-header">
      <div class="header-main">
        <h2 class="note-title">{{ note.title }}</h2>
        <div class="metadata">
          <span>Created: {{ formatDate(note.created_at) }}</span>
          <span>Last updated: {{ formatDate(note.updated_at) }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button class="icon-button" @click="saveNote" aria-label="Save changes">
            <IconSave />
        </button>
        <button class="icon-button" aria-label="More options">
            <IconDotsVertical />
        </button>
      </div>
    </header>

    <!-- Summary Panel -->
    <SummaryPanel :note="note" />

    <!-- Tags and Templates -->
    <div class="meta-controls">
        <div class="tags-section">
            <span>Add tag</span>
            <!-- Tag pills will go here -->
        </div>
        <div class="templates-section">
            <span>Recently used templates</span>
            <BaseButton variant="secondary" size="sm">+ Add Template</BaseButton>
        </div>
    </div>

    <!-- Tiptap Editor -->
    <div class="editor-wrapper">
      <TiptapToolbar v-if="editor" :editor="editor" />
      <editor-content :editor="editor" class="tiptap-editor-content" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import TextAlign from '@tiptap/extension-text-align';
import Typography from '@tiptap/extension-typography';
import { useNotebookStore } from '../../stores/notebookStore';

import BaseButton from '../ui/BaseButton.vue';
import TiptapToolbar from './TiptapToolbar.vue';
import SummaryPanel from './SummaryPanel.vue';
import IconSave from '../icons/IconSave.vue';
import IconDotsVertical from '../icons/IconDotsVertical.vue';

const store = useNotebookStore();
const note = computed(() => store.selectedNote);

const editor = useEditor({
  content: '',
  extensions: [
    StarterKit,
    Typography,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
  ],
  editorProps: {
    attributes: {
      class: 'prose prose-invert focus:outline-none',
    },
  },
});

watch(note, (newNote) => {
  if (newNote && editor.value) {
    const isSameContent = JSON.stringify(newNote.content) === JSON.stringify(editor.value.getJSON());
    if (!isSameContent) {
      editor.value.commands.setContent(newNote.content, false);
    }
  }
}, { immediate: true, deep: true });

const saveNote = async () => {
  if (!editor.value || !note.value) return;
  await store.updateNote(note.value.id, {
    title: note.value.title, // Title is not editable in this new UI
    content: editor.value.getJSON(),
  });
  // Maybe show a toast notification on success
};

const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
};

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy();
  }
});
</script>

<style lang="scss" scoped>
.note-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: var(--fluid-spacing-l);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-shrink: 0;
}

.note-title {
  font-size: var(--fluid-font-size-xxl);
  font-weight: 700;
  margin: 0 0 var(--fluid-spacing-xs) 0;
  color: var(--semantic-color-text-primary);
}

.metadata {
  display: flex;
  gap: var(--fluid-spacing-m);
  font-size: var(--fluid-font-size-s);
  color: var(--semantic-color-text-secondary);
}

.header-actions {
  display: flex;
  gap: var(--fluid-spacing-s);
  .icon-button {
    background: none;
    border: none;
    color: var(--semantic-color-text-secondary);
    cursor: pointer;
    padding: var(--fluid-spacing-xs);
    border-radius: var(--semantic-border-radius-interactive);
    &:hover {
      background-color: var(--semantic-color-surface-tertiary);
    }
  }
}

.meta-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--fluid-spacing-m);
    flex-wrap: wrap;
    font-size: var(--fluid-font-size-m);
    color: var(--semantic-color-text-secondary);
}

.tags-section, .templates-section {
    display: flex;
    align-items: center;
    gap: var(--fluid-spacing-m);
}

.editor-wrapper {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-container);
  background-color: var(--semantic-color-surface-secondary);
}

.tiptap-editor-content {
  flex-grow: 1;
  overflow-y: auto;
  padding: var(--fluid-spacing-m);
  color: var(--semantic-color-text-primary);

  .prose {
    max-width: none;
  }

  &:focus {
    outline: none;
  }
}
</style>