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
  border: 1px solid var(--semantic-color-border-neutral-subtle);
  border-radius: var(--semantic-border-radius-actions-sm);
  background-color: var(--semantic-color-surface-primary);
}

.toolbar {
  display: flex;
  gap: var(--semantic-size-gap-sm);
  padding: var(--semantic-size-inset-sm);
  border-bottom: 1px solid var(--semantic-color-border-neutral-subtle);

  button {
    font-weight: bold;
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid transparent;
    background: none;
    cursor: pointer;

    &.is-active {
      background-color: var(--semantic-color-surface-secondary);
    }
  }
}

.prose-mirror-editor {
  padding: var(--semantic-size-inset-md);
  min-height: 200px;
  outline: none;

  p {
    margin-bottom: 1em;
  }

  ul, ol {
    padding-left: 1.5rem;
    margin-bottom: 1em;
  }
}
</style>