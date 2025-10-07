<template>
  <div v-if="note" class="note-editor-container">
    <!-- Note Title -->
    <input v-model="editableTitle" class="title-input" />

    <!-- Metadata Header -->
    <div class="metadata-header">
      <div class="meta-item">
        Created: {{ formatDate(note.created_at) }}
      </div>
      <div class="meta-item">
        Updated: {{ formatDate(note.updated_at) }}
      </div>
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

    <!-- Editor Content -->
    <div class="editor-header-actions">
       <span class="save-status">{{ saveStatus }}</span>
       <button @click="saveAsTemplate" class="button-secondary" v-show="false">Save as Template</button>
    </div>
    <editor-content :editor="editor" class="tiptap-editor" />
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import { useNotebookStore } from '../../stores/notebookStore';
import DailyPnlChart from '../dashboard/widgets/charts/DailyPnlChart.vue';

const store = useNotebookStore();
const note = computed(() => store.selectedNote);
const financialData = computed(() => store.financialData);
const folder = computed(() => store.selectedNoteFolder);

const isTradeNoteFolder = computed(() => folder.value?.system_folder_identifier === 'TRADE_NOTES');
const isDailyJournalNote = computed(() => folder.value?.system_folder_identifier === 'DAILY_JOURNAL');

const editableTitle = ref(note.value ? note.value.title : '');
const saveStatus = ref(''); // To provide visual feedback on save state.

const editor = useEditor({
  content: note.value ? note.value.content : '',
  extensions: [StarterKit],
  editorProps: {
    attributes: {
      class: 'prose prose-invert focus:outline-none',
    },
  },
});

// Helper for debouncing
function debounce(fn, delay) {
  let timeoutId;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

// Helper functions for formatting
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
        // Clear the status message after a couple of seconds
        setTimeout(() => {
            saveStatus.value = '';
        }, 2000);
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
    // Trigger save only on actual changes
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
            // Optionally, show a success toast
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
  font: var(--semantic-font-style-label-xl);
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
</style>