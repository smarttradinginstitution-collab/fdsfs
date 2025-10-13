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
import Underline from '@tiptap/extension-underline';
import { ResizableImageExtension } from '@/utils/tiptap/ResizableImageExtension.js';

// Custom UI Components
import ToolbarDropdown from '../ui/ToolbarDropdown.vue';
import ToolbarColorPicker from '../ui/ToolbarColorPicker.vue';
import BaseModal from '../ui/BaseModal.vue';
import TradeImageGallery from '../images/TradeImageGallery.vue';
import ImageMetadataModal from '../images/ImageMetadataModal.vue';

// Icons
import {
  ArrowUturnLeftIcon, ArrowUturnRightIcon, MinusIcon, CodeBracketIcon, LinkIcon, ListBulletIcon, QueueListIcon, CheckCircleIcon, Bars3BottomLeftIcon, Bars2Icon, Bars3BottomRightIcon, PlusIcon, PhotoIcon
} from '@heroicons/vue/24/solid';

// Store and other components
import { useNotebookStore } from '../../stores/notebookStore';
import { useUiStore } from '../../stores/uiStore';

const store = useNotebookStore();
const uiStore = useUiStore();
const note = computed(() => store.selectedNote);
const financialData = computed(() => store.financialData);
const folder = computed(() => store.selectedNoteFolder);

const isTradeNote = computed(() => !!note.value?.trade_id);
const isDailyJournalNote = computed(() => folder.value?.system_folder_identifier === 'DAILY_JOURNAL');

const editableTitle = ref(note.value ? note.value.title : '');
const isSaving = ref(false); // Flag to prevent concurrent saves

// State for modals
const isGalleryModalOpen = ref(false);
const isMetadataModalOpen = ref(false);
const selectedImageForEdit = ref(null);


const fontFamilies = ['Arial', 'Georgia', 'Helvetica', 'Times New Roman', 'Verdana'];
const fontSizes = ['12px', '14px', '15px', '16px', '18px', '24px', '30px', '36px'];

const editor = useEditor({
  content: note.value ? note.value.content : '',
  extensions: [
    StarterKit.configure({
      heading: { levels: [1, 2, 3, 4, 5, 6] },
      link: { openOnClick: false },
    }),
    Underline,
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    FontFamily,
    TextStyle,
    Color,
    Highlight.configure({ multicolor: true }),
    TaskList,
    TaskItem.configure({ nested: true }),
    FontSize,
    ResizableImageExtension,
  ],
  editorProps: {
    attributes: { class: 'prose prose-invert focus:outline-none' },
  },
});

// --- Toolbar Logic ---
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

const openImageGallery = () => {
  if (isTradeNote.value) {
    isGalleryModalOpen.value = true;
  }
};

const handleInsertImage = (imageUrl) => {
  if (editor.value) {
    editor.value.chain().focus().setResizableImage({ src: imageUrl }).run();
    isGalleryModalOpen.value = false;
  }
};

const handleEditImage = (image) => {
  selectedImageForEdit.value = image;
  isMetadataModalOpen.value = true;
};

// --- Core Component Logic ---
function debounce(fn, delay) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const formatCurrency = (value) => {
  if (typeof value !== 'number') return 'N/A';
  return value.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  });
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
        col1: [ { label: 'Total Trades', value: stats.trade_count }, { label: 'Winrate', value: `${stats.win_rate.toFixed(1)}%` } ],
        col2: [ { label: 'Winners', value: stats.winning_trades }, { label: 'Losers', value: stats.losing_trades }, ],
        col3: [
          { label: 'Gross Profit', value: formattedPnl(stats.gross_profit), rawValue: stats.gross_profit, isPnl: true },
          { label: 'Gross Loss', value: formattedPnl(stats.gross_loss), rawValue: stats.gross_loss, isPnl: true },
        ],
        col4: [ { label: 'Net P&L', value: formattedPnl(stats.net_pnl), rawValue: stats.net_pnl, isPnl: true }, { label: 'Profit Factor', value: stats.profit_factor_label } ]
    };
});

watch(note, (newNote, oldNote) => {
  if (newNote && editor.value) {
    if (!oldNote || newNote.id !== oldNote.id) {
      editableTitle.value = newNote.title;
      if (JSON.stringify(newNote.content) !== JSON.stringify(editor.value.getJSON())) {
          editor.value.commands.setContent(newNote.content, false);
      }
    }
  } else if (!newNote && editor.value) {
    editableTitle.value = '';
    editor.value.commands.clearContent();
  }
}, { deep: true });

const saveNote = async () => {
    if (!editor.value || !note.value || isSaving.value) return;

    isSaving.value = true;
    try {
        await store.updateNote(note.value.id, {
            title: editableTitle.value,
            content: editor.value.getJSON(),
        });
        uiStore.showNotification({ message: 'Note saved!', type: 'success', size: 'small' });
    } catch (error) {
        console.error("Failed to save note:", error);
        uiStore.showNotification({ message: 'Error saving note.', type: 'error' });
    } finally {
        isSaving.value = false;
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
    if (confirm("Save the current content as the template for this folder? This will overwrite any existing template.")) {
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
    <input v-model="editableTitle" class="title-input" />

    <div class="metadata-header">
      <div class="meta-item">Created: {{ formatDate(note.created_at) }}</div>
      <div class="meta-item">Updated: {{ formatDate(note.updated_at) }}</div>
    </div>

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

    <div v-if="isTradeNote" class="financial-details">
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

    <div v-if="isDailyJournalNote && statsGrid" class="daily-summary-container">
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

    <div class="editor-header-actions">
       <button @click="saveAsTemplate" class="button-secondary" v-show="false">Save as Template</button>
    </div>

    <div class="tiptap-wrapper">
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
        <button @click="openImageGallery" :disabled="!isTradeNote" class="icon-button" title="Add image from trade gallery">
          <PhotoIcon class="h-5 w-5" />
        </button>
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

    <BaseModal :show="isGalleryModalOpen" @close="isGalleryModalOpen = false" title="Trade Image Gallery">
      <TradeImageGallery
        v-if="isGalleryModalOpen && note.trade_id"
        :trade-id="note.trade_id"
        mode="full"
        @insert-image="handleInsertImage"
        @edit-image="handleEditImage"
      />
    </BaseModal>

    <ImageMetadataModal
      :show="isMetadataModalOpen"
      :image="selectedImageForEdit"
      @close="isMetadataModalOpen = false"
    />
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

.daily-summary-container {
  padding: var(--semantic-size-inset-sm);
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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

.button-secondary {
    padding: 0.5rem 1rem;
    border-radius: var(--semantic-border-radius-interactive);
    cursor: pointer;
    border: 1px solid transparent;
    transition: background-color 0.2s;
    background-color: var(--semantic-color-surface-secondary);
    color: var(--semantic-color-text-primary);
    border-color: var(--semantic-color-border-default);
}

.button-secondary:hover {
    background-color: var(--semantic-color-surface-tertiary);
}

.tiptap-wrapper {
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tiptap-editor {
  flex-grow: 1;
  padding: 2rem;
  overflow-y: auto;
  .prose {
    max-width: none;
  }

  img {
    max-width: 100%;
    height: auto;
    border-radius: var(--semantic-border-radius-container);
  }

  ul[data-type="taskList"] {
    list-style: none;
    padding: 0;
    margin: 1rem 0;

    li {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.5rem;

      > label {
        padding-top: 0.25em;
      }

      > div {
        flex-grow: 1;

        p {
          margin-top: 0;
        }
      }
    }
  }
}
</style>