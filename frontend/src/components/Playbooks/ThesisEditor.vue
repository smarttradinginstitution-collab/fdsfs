
<template>
  <div class="thesis-editor">
    <div v-if="editor" class="tiptap-wrapper">
      <div class="toolbar">
        <button @click="editor.chain().focus().undo().run()" :disabled="!editor.can().undo()" class="icon-button"><ArrowUturnLeftIcon class="h-5 w-5" /></button>
        <button @click="editor.chain().focus().redo().run()" :disabled="!editor.can().redo()" class="icon-button"><ArrowUturnRightIcon class="h-5 w-5" /></button>
        <div class="divider"></div>
        <ToolbarDropdown v-model="activeHeading" :items="headingItems" />
        <ToolbarDropdown v-model="activeFontFamily" :items="fontFamilyItems" />
        <ToolbarDropdown v-model="activeFontSize" :items="fontSizeItems" />
        <div class="divider"></div>
        <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }" class="icon-button text-button">B</button>
        <button @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }" class="icon-button text-button">I</button>
        <button @click="editor.chain().focus().toggleUnderline().run()" :class="{ 'is-active': editor.isActive('underline') }" class="icon-button text-button">U</button>
        <button @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }" class="icon-button"><MinusIcon class="h-5 w-5" /></button>
        <button @click="editor.chain().focus().toggleCode().run()" :class="{ 'is-active': editor.isActive('code') }" class="icon-button"><CodeBracketIcon class="h-5 w-5" /></button>
        <button @click="setLink" :class="{ 'is-active': editor.isActive('link') }" class="icon-button"><LinkIcon class="h-5 w-5" /></button>
        <div class="divider"></div>
        <ToolbarColorPicker v-model="textColor"><span class="font-bold">A</span></ToolbarColorPicker>
        <ToolbarColorPicker v-model="highlightColor"><span class="font-bold" :style="{ backgroundColor: highlightColor, padding: '2px' }">Aa</span></ToolbarColorPicker>
        <button class="icon-button"><PlusIcon class="h-5 w-5" /></button>
        <div class="divider"></div>
        <button @click="editor.chain().focus().toggleBulletList().run()" :class="{ 'is-active': editor.isActive('bulletList') }" class="icon-button"><ListBulletIcon class="h-5 w-5" /></button>
        <button @click="editor.chain().focus().toggleOrderedList().run()" :class="{ 'is-active': editor.isActive('orderedList') }" class="icon-button"><QueueListIcon class="h-5 w-5" /></button>
        <button @click="editor.chain().focus().toggleTaskList().run()" :class="{ 'is-active': editor.isActive('taskList') }" class="icon-button"><CheckCircleIcon class="h-5 w-5" /></button>
        <div class="divider"></div>
        <button @click="editor.chain().focus().setTextAlign('left').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }" class="icon-button"><Bars3BottomLeftIcon class="h-5 w-5" /></button>
        <button @click="editor.chain().focus().setTextAlign('center').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }" class="icon-button"><Bars2Icon class="h-5 w-5" /></button>
        <button @click="editor.chain().focus().setTextAlign('right').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }" class="icon-button"><Bars3BottomRightIcon class="h-5 w-5" /></button>
      </div>
      <editor-content :editor="editor" class="tiptap-editor" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue';
import { useTiptapEditor } from '@/composables/useTiptapEditor';
import { EditorContent } from '@tiptap/vue-3';
import ToolbarDropdown from '../ui/ToolbarDropdown.vue';
import ToolbarColorPicker from '../ui/ToolbarColorPicker.vue';
import {
  ArrowUturnLeftIcon, ArrowUturnRightIcon, MinusIcon, CodeBracketIcon, LinkIcon, ListBulletIcon, QueueListIcon, CheckCircleIcon, Bars3BottomLeftIcon, Bars2Icon, Bars3BottomRightIcon, PlusIcon
} from '@heroicons/vue/24/solid';

const props = defineProps({
  content: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['update:content']);

const { editor } = useTiptapEditor(props.content.html);

const fontFamilies = ['Arial', 'Georgia', 'Helvetica', 'Times New Roman', 'Verdana'];
const fontSizes = ['12px', '14px', '15px', '16px', '18px', '24px', '30px', '36px'];

const headingItems = computed(() => [
  { label: 'Paragraph', value: 0, isActive: () => editor.value.isActive('paragraph') },
  ...[1, 2, 3, 4, 5, 6].map(level => ({
    label: `Heading ${level}`, value: level, isActive: () => editor.value.isActive('heading', { level }),
  })),
]);

const fontFamilyItems = computed(() => fontFamilies.map(font => ({
  label: font.split(',')[0], value: font, isActive: () => editor.value.isActive('textStyle', { fontFamily: font }),
})));

const fontSizeItems = computed(() => fontSizes.map(size => ({
  label: `${size.replace('px', '')}px`, value: size, isActive: () => editor.value.isActive('textStyle', { fontSize: size }),
})));

const activeHeading = computed({
  get: () => headingItems.value.find(item => item.isActive())?.value ?? 0,
  set: (value) => {
    if (value === 0) editor.value.chain().focus().setParagraph().run();
    else editor.value.chain().focus().toggleHeading({ level: value }).run();
  },
});

const activeFontFamily = computed({
  get: () => fontFamilyItems.value.find(item => item.isActive())?.value ?? fontFamilies[0],
  set: (value) => editor.value.chain().focus().setFontFamily(value).run(),
});

const activeFontSize = computed({
  get: () => fontSizeItems.value.find(item => item.isActive())?.value ?? '16px',
  set: (value) => editor.value.chain().focus().setFontSize(value).run(),
});

const textColor = computed({
  get: () => editor.value?.getAttributes('textStyle').color || '#000000',
  set: (value) => editor.value.chain().focus().setColor(value).run(),
});

const highlightColor = computed({
  get: () => editor.value?.getAttributes('highlight').color || 'transparent',
  set: (value) => editor.value.chain().focus().toggleHighlight({ color: value }).run(),
});

const setLink = () => {
  const url = window.prompt('URL', editor.value.getAttributes('link').href);
  if (url === null) return;
  if (url === '') editor.value.chain().focus().extendMarkRange('link').unsetLink().run();
  else editor.value.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
};

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

  .icon-button {
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

    &:disabled {
      color: var(--semantic-color-text-disabled);
      cursor: not-allowed;
      background-color: transparent;
    }
  }
  .text-button {
    font-weight: bold;
    font-size: 0.9rem;
  }

  .divider {
    width: 1px;
    height: 1.25rem;
    background-color: var(--semantic-color-border-default);
    margin: 0 0.6rem;
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
