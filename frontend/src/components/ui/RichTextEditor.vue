<script setup>
import { defineProps, defineEmits, watch } from 'vue';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['update:modelValue']);

const editor = useEditor({
  content: props.modelValue,
  extensions: [StarterKit],
  onUpdate: () => {
    emit('update:modelValue', editor.value.getHTML());
  },
  editorProps: {
    attributes: {
      class: 'prose-mirror-editor',
    },
  },
});

watch(() => props.modelValue, (value) => {
  const isSame = editor.value.getHTML() === value;
  if (isSame) {
    return;
  }
  editor.value.commands.setContent(value, false);
});

const toggleBold = () => editor.value.chain().focus().toggleBold().run();
const toggleItalic = () => editor.value.chain().focus().toggleItalic().run();
const toggleStrike = () => editor.value.chain().focus().toggleStrike().run();
const toggleBulletList = () => editor.value.chain().focus().toggleBulletList().run();
const toggleOrderedList = () => editor.value.chain().focus().toggleOrderedList().run();

</script>

<template>
  <div v-if="editor" class="rich-text-editor">
    <div class="toolbar">
      <button @click="toggleBold" :class="{ 'is-active': editor.isActive('bold') }">B</button>
      <button @click="toggleItalic" :class="{ 'is-active': editor.isActive('italic') }">I</button>
      <button @click="toggleStrike" :class="{ 'is-active': editor.isActive('strike') }">S</button>
      <button @click="toggleBulletList" :class="{ 'is-active': editor.isActive('bulletList') }">UL</button>
      <button @click="toggleOrderedList" :class="{ 'is-active': editor.isActive('orderedList') }">OL</button>
    </div>
    <EditorContent :editor="editor" />
  </div>
</template>

<style lang="scss">
.rich-text-editor {
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  background-color: var(--semantic-color-surface-primary);
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-xs);
  padding: var(--semantic-size-inset-sm);
  border-bottom: 1px solid var(--semantic-color-border-default);

  button {
    font-weight: bold;
    padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
    border-radius: var(--semantic-border-radius-interactive);
    border: 1px solid transparent;
    background-color: transparent;
    color: var(--semantic-color-text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background-color: var(--semantic-color-surface-secondary);
      color: var(--semantic-color-text-primary);
    }

    &.is-active {
      background-color: var(--semantic-color-interactive-primary-default);
      color: var(--semantic-color-text-on-brand);
    }
  }
}

.prose-mirror-editor {
  padding: var(--semantic-size-inset-md);
  flex-grow: 1;
  outline: none;
  overflow-y: auto;
  line-height: var(--base-font-line-height-loose);

  > :first-child {
    margin-top: 0;
  }

  p {
    margin-bottom: 1em;
  }

  ul, ol {
    padding-left: 1.5rem;
    margin-bottom: 1em;
  }

  h1, h2, h3 {
    margin-bottom: 0.5em;
    font-weight: var(--base-font-weight-semibold);
  }
}
</style>