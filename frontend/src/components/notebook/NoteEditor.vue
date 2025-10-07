<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import TextAlign from '@tiptap/extension-text-align';
import FontFamily from '@tiptap/extension-font-family';
import { TextStyle } from '@tiptap/extension-text-style';
import { Color } from '@tiptap/extension-color';
import Highlight from '@tiptap/extension-highlight';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import { FontSize } from '@/utils/tiptap/FontSize.js';

// Custom UI Components
import ToolbarDropdown from '../ui/ToolbarDropdown.vue';
import ToolbarColorPicker from '../ui/ToolbarColorPicker.vue';

// Icons
import {
  ArrowUturnLeftIcon, ArrowUturnRightIcon, MinusIcon, CodeBracketIcon, LinkIcon, ListBulletIcon, QueueListIcon, CheckCircleIcon, Bars3BottomLeftIcon, Bars2Icon, Bars3BottomRightIcon, PlusIcon
} from '@heroicons/vue/24/solid';

// Store and other components
import { useNotebookStore } from '../../stores/notebookStore';
import DailyPnlChart from '../dashboard/widgets/charts/DailyPnlChart.vue';

const store = useNotebookStore();
const note = computed(() => store.selectedNote);
const financialData = computed(() => store.financialData);
const folder = computed(() => store.selectedNoteFolder);

const isTradeNoteFolder = computed(() => folder.value?.system_folder_identifier === 'TRADE_NOTES');
const isDailyJournalNote = computed(() => folder.value?.system_folder_identifier === 'DAILY_JOURNAL');

const editableTitle = ref(note.value ? note.value.title : '');
const saveStatus = ref('');

const fontFamilies = ['Arial', 'Georgia', 'Helvetica', 'Times New Roman', 'Verdana'];
const fontSizes = ['12px', '14px', '15px', '16px', '18px', '24px', '30px', '36px'];

const editor = useEditor({
  content: note.value ? note.value.content : '',
  extensions: [
    StarterKit.configure({
      heading: { levels: [1, 2, 3, 4, 5, 6] },
      link: {
        openOnClick: false,
      },
    }),
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    FontFamily,
    TextStyle,
    Color,
    Highlight.configure({ multicolor: true }),
    TaskList,
    TaskItem.configure({ nested: true }),
    FontSize,
  ],
  editorProps: {
    attributes: { class: 'prose prose-invert focus:outline-none' },
  },
});

// --- Toolbar Logic ---
const headingItems = computed(() => [
  { label: 'Paragraph', value: 0, isActive: () => editor.value.isActive('paragraph') },
  ...[1, 2, 3, 4, 5, 6].map(level => ({
    label: `Heading ${level}`,
    value: level,
    isActive: () => editor.value.isActive('heading', { level }),
  })),
]);

const fontFamilyItems = computed(() => fontFamilies.map(font => ({
  label: font.split(',')[0],
  value: font,
  isActive: () => editor.value.isActive('textStyle', { fontFamily: font }),
})));

const fontSizeItems = computed(() => fontSizes.map(size => ({
  label: `${size.replace('px', '')}px`,
  value: size,
  isActive: () => editor.value.isActive('textStyle', { fontSize: size }),
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
  if (url === '') {
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run();
  } else {
    editor.value.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
  }
};

// --- Core Component Logic ---
function debounce(fn, delay) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

const formatDate = (dateString) => new Date(dateString).toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
const formatCurrency = (value) => typeof value === 'number' ? value.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) : 'N/A';
const formatPercentage = (value) => typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : 'N/A';
const pnlClass = (pnl) => typeof pnl !== 'number' ? 'pnl-neutral' : (pnl >= 0 ? 'pnl-positive' : 'pnl-negative');
const formattedPnl = (pnl) => {
  if (pnl == null) return '$0.00';
  const sign = pnl >= 0 ? '+' : '-';
  return `${sign}$${Math.abs(pnl).toFixed(2)}`;
};

const statsGrid = computed(() => {
  if (!financialData.value?.stats) return null;
  const { stats } = financialData.value;
  return {
    col1: [{ label: 'Total Trades', value: stats.trade_count }, { label: 'Winrate', value: `${stats.win_rate.toFixed(1)}%` }],
    col2: [{ label: 'Winners', value: stats.winning_trades }, { label: 'Losers', value: stats.losing_trades }],
    col3: [{ label: 'Gross Profit', value: formattedPnl(stats.gross_profit), rawValue: stats.gross_profit, isPnl: true }, { label: 'Gross Loss', value: formattedPnl(stats.gross_loss), rawValue: stats.gross_loss, isPnl: true }],
    col4: [{ label: 'Net P&L', value: formattedPnl(stats.net_pnl), rawValue: stats.net_pnl, isPnl: true }, { label: 'Profit Factor', value: stats.profit_factor_label }],
  };
});

const saveNote = async () => {
  if (!editor.value || !note.value) return;
  saveStatus.value = 'Saving...';
  try {
    await store.updateNote(note.value.id, { title: editableTitle.value, content: editor.value.getJSON() });
    saveStatus.value = 'Saved!';
    setTimeout(() => { saveStatus.value = ''; }, 2000);
  } catch (error) {
    console.error("Failed to save note:", error);
    saveStatus.value = 'Error!';
  }
};

const debouncedSave = debounce(saveNote, 1500);

watch(note, (newNote) => {
  if (newNote && editor.value) {
    editableTitle.value = newNote.title;
    if (JSON.stringify(newNote.content) !== JSON.stringify(editor.value.getJSON())) {
      editor.value.commands.setContent(newNote.content, false);
    }
  }
}, { deep: true });

watch([editableTitle, () => editor.value?.getHTML()], () => {
  debouncedSave();
}, { deep: true });

onBeforeUnmount(() => {
  if (editor.value) editor.value.destroy();
});
</script>

<template>
  <div v-if="note && editor" class="note-editor-container">
    <input v-model="editableTitle" class="title-input" />

    <div class="metadata-header">
      <div class="meta-item">Created: {{ formatDate(note.created_at) }}</div>
      <div class="meta-item">Updated: {{ formatDate(note.updated_at) }}</div>
    </div>

    <!-- Toolbar -->
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

    <div class="editor-header-actions">
       <span class="save-status">{{ saveStatus }}</span>
    </div>
    <editor-content :editor="editor" class="tiptap-editor" />
  </div>
</template>

<style lang="scss">
.note-editor-container {
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  background: var(--semantic-color-surface-primary);
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.title-input {
  font: var(--semantic-font-style-heading-xl);
  font-weight: bold;
  background: transparent;
  border: none;
  color: var(--semantic-color-text-primary);
  padding: 0.25rem 0;
  &:focus {
    outline: none;
    box-shadow: 0 1px 0 var(--semantic-color-border-focus);
  }
}

.metadata-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--semantic-color-text-secondary);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  padding: 0.25rem 0.5rem;
  background-color: var(--semantic-color-surface-secondary);
  border-radius: var(--semantic-border-radius-interactive);
  border: 1px solid var(--semantic-color-border-default);

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

.editor-header-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.save-status {
  font-size: 0.875rem;
  color: var(--semantic-color-text-secondary);
}

.tiptap-editor {
  flex-grow: 1;
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: 1rem;
  overflow-y: auto;
  .prose {
    max-width: none;
  }
}
</style>