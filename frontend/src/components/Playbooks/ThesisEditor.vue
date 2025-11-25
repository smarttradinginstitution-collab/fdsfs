
<template>
  <div class="thesis-editor">
    <div v-if="editor" class="tiptap-wrapper">
      <div class="toolbar">
        <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }">Bold</button>
        <button @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }">Italic</button>
        <button @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }">Strike</button>
      </div>
      <editor-content :editor="editor" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from 'vue';
import { useTiptapEditor } from '@/composables/useTiptapEditor';
import { EditorContent } from '@tiptap/vue-3';

const props = defineProps({
  content: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['update:content']);

const { editor } = useTiptapEditor(props.content.html);

watch(() => props.content, (newContent) => {
  if (editor.value && newContent.html !== editor.value.getHTML()) {
    editor.value.commands.setContent(newContent.html, false);
  }
}, { deep: true });

watch(() => editor.value?.getHTML(), (newContent) => {
  if (newContent !== props.content.html) {
    emit('update:content', { ...props.content, html: newContent });
  }
});

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy();
  }
});
</script>

<style lang="scss" scoped>
.thesis-editor {
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  background: var(--semantic-color-surface-primary);
  padding: 1rem;
}

.tiptap-wrapper {
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  padding: 0.1rem 0.1rem;
  border-bottom: 1px solid var(--semantic-color-border-default);

  button {
    background: none;
    border: none;
    padding: 0.4rem;
    margin: 0 0.1rem;
    cursor: pointer;
    border-radius: 4px;
    color: var(--semantic-color-text-primary);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 28px;
    min-height: 28px;

    &:hover {
      background-color: var(--semantic-color-surface-tertiary);
    }

    &.is-active {
      background-color: var(--semantic-color-surface-tertiary);
      color: var(--semantic-color-text-focus);
    }
  }
}

:deep(.tiptap-editor) {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
  .prose {
    max-width: none;
  }
}
</style>
