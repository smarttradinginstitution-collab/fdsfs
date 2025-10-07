<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import TextAlign from '@tiptap/extension-text-align';
import FontFamily from '@tiptap/extension-font-family';
import { TextStyle } from '@tiptap/extension-text-style';
import { Color } from '@tiptap/extension-color';
import Highlight from '@tiptap/extension-highlight';
import Link from '@tiptap/extension-link';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import { FontSize } from '@/utils/tiptap/FontSize.js';

import {
  ArrowUturnLeftIcon, ArrowUturnRightIcon, BoldIcon, ItalicIcon, UnderlineIcon, MinusIcon, CodeBracketIcon, LinkIcon, ListBulletIcon, QueueListIcon, CheckCircleIcon, Bars3BottomLeftIcon, Bars2Icon, Bars3BottomRightIcon, ChevronDownIcon
} from '@heroicons/vue/24/solid';

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
const fontSizes = ['12px', '14px', '16px', '18px', '24px', '30px', '36px'];

const editor = useEditor({
  content: note.value ? note.value.content : '',
  extensions: [
    StarterKit.configure({
      heading: { levels: [1, 2, 3, 4, 5, 6] },
    }),
    Underline,
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    FontFamily,
    TextStyle,
    Color,
    Highlight.configure({ multicolor: true }),
    Link.configure({ openOnClick: false }),
    TaskList,
    TaskItem.configure({ nested: true }),
    FontSize,
  ],
  editorProps: {
    attributes: {
      class: 'prose prose-invert focus:outline-none',
    },
  },
});

const handleHeadingChange = (event) => {
  const level = parseInt(event.target.value, 10);
  if (level === 0) {
    editor.value.chain().focus().setParagraph().run();
  } else {
    editor.value.chain().focus().toggleHeading({ level }).run();
  }
};

const setLink = () => {
  const previousUrl = editor.value.getAttributes('link').href;
  const url = window.prompt('URL', previousUrl);
  if (url === null) return;
  if (url === '') {
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run();
    return;
  }
  editor.value.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
};

function debounce(fn, delay) {
  let timeoutId;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  });
};

const formatCurrency = (value) => {
  if (typeof value !== 'number') return 'N/A';
  return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
};

const formatPercentage = (value) => {
  if (typeof value !== 'number') return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
};

const pnlClass = (pnl) => {
  if (typeof pnl !== 'number') return 'pnl-neutral';
  return pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
};

const formattedPnl = (pnl) => {
  if (pnl === null || pnl === undefined) return '$0.00';
  const sign = pnl >= 0 ? '+' : '-';
  return `${sign}$${Math.abs(pnl).toFixed(2)}`;
};

const statsGrid = computed(() => {
  if (!financialData.value || !financialData.value.stats) return null;
  const stats = financialData.value.stats;
  return {
    col1: [{ label: 'Total Trades', value: stats.trade_count }, { label: 'Winrate', value: `${stats.win_rate.toFixed(1)}%` }],
    col2: [{ label: 'Winners', value: stats.winning_trades }, { label: 'Losers', value: stats.losing_trades }],
    col3: [{ label: 'Gross Profit', value: formattedPnl(stats.gross_profit), rawValue: stats.gross_profit, isPnl: true }, { label: 'Gross Loss', value: formattedPnl(stats.gross_loss), rawValue: stats.gross_loss, isPnl: true }],
    col4: [{ label: 'Net P&L', value: formattedPnl(stats.net_pnl), rawValue: stats.net_pnl, isPnl: true }, { label: 'Profit Factor', value: stats.profit_factor_label }],
  };
});

watch(note, (newNote) => {
  if (newNote && editor.value) {
    editableTitle.value = newNote.title;
    if (JSON.stringify(newNote.content) !== JSON.stringify(editor.value.getJSON())) {
      editor.value.commands.setContent(newNote.content, false);
    }
  }
}, { deep: true });

const saveNote = async () => {
  if (!editor.value || !note.value) return;
  saveStatus.value = 'Saving...';
  try {
    await store.updateNote(note.value.id, {
      title: editableTitle.value,
      content: editor.value.getJSON(),
    });
    saveStatus.value = 'Saved!';
    setTimeout(() => { saveStatus.value = ''; }, 2000);
  } catch (error) {
    console.error("Failed to save note:", error);
    saveStatus.value = 'Error!';
  }
};

const debouncedSave = debounce(saveNote, 1500);

watch(editableTitle, (newTitle) => {
  if (note.value && newTitle !== note.value.title) {
    debouncedSave();
  }
});

watch(() => editor.value?.getHTML(), (newContent, oldContent) => {
  if (newContent !== oldContent && note.value) {
    debouncedSave();
  }
}, { deep: true });

const saveAsTemplate = async () => {
  if (!editor.value || !note.value) return;
  if (confirm("Save current content as template?")) {
    try {
      await store.saveFolderTemplate({
        folderId: note.value.folder_id,
        templateContent: editor.value.getJSON(),
      });
    } catch (error) {
      console.error("Failed to save template:", error);
    }
  }
};

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy();
  }
});
</script>

<template>
  <div v-if="note && editor" class="note-editor-container">
    <!-- Note Title -->
    <input v-model="editableTitle" class="title-input" />

    <!-- Metadata Header -->
    <div class="metadata-header">
      <div class="meta-item">Created: {{ formatDate(note.created_at) }}</div>
      <div class="meta-item">Updated: {{ formatDate(note.updated_at) }}</div>
    </div>

    <!-- P&L and Actions Display -->
    <div class="pnl-container" v-if="financialData">
      <div class="pnl-display">
        <strong>Net P&L: </strong>
        <span :class="pnlClass(financialData?.net_pnl)">
          {{ formatCurrency(financialData?.net_pnl) }}
        </span>
      </div>
      <router-link
        v-if="note && note.trade_id"
        :to="{ name: 'report-detail', params: { id: note.trade_id } }"
        class="details-button"
      >
        Trade Details
      </router-link>
    </div>

    <!-- Financial Details Section (only for Trade Notes) -->
    <div v-if="isTradeNoteFolder" class="financial-details">
      <div class="detail-card">
        <label>Gross P&L</label>
        <span>{{ formatCurrency(financialData?.gross_pnl) }}</span>
      </div>
      <div class="detail-card">
        <label>Commissions</label>
        <span>{{ formatCurrency(financialData?.total_commissions) }}</span>
      </div>
      <div class="detail-card">
        <label>Net ROI</label>
        <span>{{ formatPercentage(financialData?.net_roi) }}</span>
      </div>
    </div>

    <!-- Daily Journal Summary Section -->
    <div v-if="isDailyJournalNote && statsGrid" class="daily-summary-container">
      <div class="chart-section">
        <DailyPnlChart :chart-data="financialData.cumulative_pnl_series" />
      </div>
      <div class="stats-section">
        <div class="stat-col" v-for="col in statsGrid" :key="col[0].label">
          <div v-for="stat in col" :key="stat.label" class="stat-cell">
            <span class="stat-label">{{ stat.label }}</span>
            <span v-if="stat.isPnl" class="stat-value" :style="pnlClass(stat.rawValue)">{{ stat.value }}</span>
            <span v-else class="stat-value">{{ stat.value }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <button @click="editor.chain().focus().undo().run()" :disabled="!editor.can().undo()"><ArrowUturnLeftIcon class="h-5 w-5" /></button>
      <button @click="editor.chain().focus().redo().run()" :disabled="!editor.can().redo()"><ArrowUturnRightIcon class="h-5 w-5" /></button>
      <div class="divider"></div>
      <select @change="handleHeadingChange($event)" class="toolbar-select">
        <option value="0">Paragraph</option>
        <option v-for="level in 6" :key="level" :value="level" :selected="editor.isActive('heading', { level })">Heading {{ level }}</option>
      </select>
      <div class="divider"></div>
      <select @change="editor.chain().focus().setFontFamily($event.target.value).run()" class="toolbar-select">
        <option v-for="font in fontFamilies" :key="font" :value="font" :selected="editor.isActive('textStyle', { fontFamily: font })">{{ font.split(',')[0] }}</option>
      </select>
      <select @change="editor.chain().focus().setFontSize($event.target.value).run()" class="toolbar-select">
        <option v-for="size in fontSizes" :key="size" :value="size" :selected="editor.isActive('textStyle', { fontSize: size })">{{ size.replace('px', '') }}</option>
      </select>
      <div class="divider"></div>
      <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }"><BoldIcon class="h-5 w-5" /></button>
      <button @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }"><ItalicIcon class="h-5 w-5" /></button>
      <button @click="editor.chain().focus().toggleUnderline().run()" :class="{ 'is-active': editor.isActive('underline') }"><UnderlineIcon class="h-5 w-5" /></button>
      <button @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }"><MinusIcon class="h-5 w-5" /></button>
      <button @click="editor.chain().focus().toggleCode().run()" :class="{ 'is-active': editor.isActive('code') }"><CodeBracketIcon class="h-5 w-5" /></button>
      <button @click="setLink" :class="{ 'is-active': editor.isActive('link') }"><LinkIcon class="h-5 w-5" /></button>
      <div class="divider"></div>
      <div class="color-picker-wrapper">
        <input type="color" @input="editor.chain().focus().setColor($event.target.value).run()" :value="editor.getAttributes('textStyle').color || '#000000'">
        <ChevronDownIcon class="h-5 w-5" />
      </div>
      <div class="color-picker-wrapper">
        <input type="color" @input="editor.chain().focus().toggleHighlight({ color: $event.target.value }).run()" :value="editor.getAttributes('highlight').color || '#ffff00'">
        <ChevronDownIcon class="h-5 w-5" />
      </div>
      <div class="divider"></div>
      <button @click="editor.chain().focus().toggleBulletList().run()" :class="{ 'is-active': editor.isActive('bulletList') }"><ListBulletIcon class="h-5 w-5" /></button>
      <button @click="editor.chain().focus().toggleOrderedList().run()" :class="{ 'is-active': editor.isActive('orderedList') }"><QueueListIcon class="h-5 w-5" /></button>
      <button @click="editor.chain().focus().toggleTaskList().run()" :class="{ 'is-active': editor.isActive('taskList') }"><CheckCircleIcon class="h-5 w-5" /></button>
      <div class="divider"></div>
      <button @click="editor.chain().focus().setTextAlign('left').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }"><Bars3BottomLeftIcon class="h-5 w-5" /></button>
      <button @click="editor.chain().focus().setTextAlign('center').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }"><Bars2Icon class="h-5 w-5" /></button>
      <button @click="editor.chain().focus().setTextAlign('right').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }"><Bars3BottomRightIcon class="h-5 w-5" /></button>
    </div>

    <!-- Editor Content -->
    <div class="editor-header-actions">
       <span class="save-status">{{ saveStatus }}</span>
       <button @click="saveAsTemplate" class="button-secondary" v-show="false">Save as Template</button>
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
  gap: 1rem; /* Add gap between all flex children */
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
  flex-wrap: nowrap;
}
.meta-item strong {
  color: var(--semantic-color-text-primary);
}
.pnl-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pnl-display {
  font: var(--semantic-font-style-label-xl);
  font-weight: 500;
  color: var(--semantic-color-text-secondary);
}
.pnl-display strong {
  color: var(--semantic-color-text-primary);
}
.pnl-positive {
  color: var(--semantic-color-feedback-positive-text);
}
.pnl-negative {
  color: var(--semantic-color-feedback-negative-text);
}
.pnl-neutral {
  color: var(--semantic-color-text-secondary);
}
.financial-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  padding: 1rem;
}
.detail-card {
  display: flex;
  flex-direction: column;
}
.detail-card label {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
}
.detail-card span {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);
}
.editor-header-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end; /* Align save status to the right */
    gap: 0.5rem;
}
.save-status {
    font-size: 0.875rem;
    color: var(--semantic-color-text-secondary);
    min-width: 80px; // Reserve space to prevent layout shift
    text-align: right;
}
.button-save, .button-cancel, .button-secondary {
    padding: 0.5rem 1rem;
    border-radius: var(--semantic-border-radius-interactive);
    cursor: pointer;
    border: 1px solid transparent;
    transition: background-color 0.2s;
}
.button-save {
    background-color: var(--semantic-color-interactive-primary-default);
    color: white;
    border-color: transparent;
}
.button-cancel, .button-secondary {
    background-color: var(--semantic-color-surface-secondary);
    color: var(--semantic-color-text-primary);
    border-color: var(--semantic-color-border-default);
}
.button-cancel:hover, .button-secondary:hover {
    background-color: var(--semantic-color-surface-tertiary);
}
.details-button {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-interactive);
  text-decoration: none;
  transition: all 0.2s ease;

  &:hover {
    background-color: var(--semantic-color-surface-tertiary);
    color: var(--semantic-color-text-primary);
    border-color: var(--semantic-color-border-focus);
  }
}
.tiptap-editor {
    flex-grow: 1;
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-interactive);
    padding: 1rem;
    overflow-y: auto;
}
/* Tiptap default styles override */
.prose {
    max-width: none;
}
/* Daily Summary Styles */
.daily-summary-container {
  padding: var(--semantic-size-inset-sm);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-gap-md);
}
.chart-section {
  min-height: 150px;
}
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 4 columns for desktop */
  overflow: hidden;
}
.stat-col {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
  padding: var(--semantic-size-inset-sm);
  border-right: 1px solid var(--semantic-color-border-default);
  &:last-child {
    border-right: none;
  }
}
.stat-cell {
  display: flex;
  flex-direction: column;
  gap: var(--base-size-spacing-0-5);
}
.stat-label {
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
}
.stat-value {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-primary);
  font-weight: 600;
}

/* NEW TOOLBAR STYLES */
.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  padding: 0.5rem;
  background-color: var(--semantic-color-surface-secondary);
  border-bottom: 1px solid var(--semantic-color-border-default);
  border-top: 1px solid var(--semantic-color-border-default);

  button {
    background: none;
    border: none;
    padding: 0.4rem;
    margin-right: 0.2rem;
    cursor: pointer;
    border-radius: 4px;
    color: var(--semantic-color-text-primary);

    &:hover {
      background-color: var(--semantic-color-surface-tertiary);
    }

    &.is-active {
      background-color: var(--semantic-color-surface-tertiary);
    }
  }

  .divider {
      width: 1px;
      height: 1.25rem;
      background-color: var(--semantic-color-border-default);
      margin-left: 0.5rem;
      margin-right: 0.5rem;
  }

  .toolbar-select {
      border: 1px solid var(--semantic-color-border-default);
      border-radius: 4px;
      padding: 0.3rem;
      margin-right: 0.5rem;
      background-color: var(--semantic-color-surface-primary);
      color: var(--semantic-color-text-primary);
  }

  .color-picker-wrapper {
      position: relative;
      display: flex;
      align-items: center;
      margin-right: 0.5rem;

      input[type="color"] {
          -webkit-appearance: none;
          -moz-appearance: none;
          appearance: none;
          width: 28px;
          height: 28px;
          padding: 0;
          border: none;
          background-color: transparent;
          cursor: pointer;
      }
      input[type="color"]::-webkit-color-swatch-wrapper {
          padding: 0;
      }
      input[type="color"]::-webkit-color-swatch {
          border: 1px solid var(--semantic-color-border-default);
          border-radius: 4px;
      }

      .h-5.w-5 {
          position: absolute;
          right: 4px;
          pointer-events: none;
          color: var(--semantic-color-text-secondary);
      }
  }
}
</style>