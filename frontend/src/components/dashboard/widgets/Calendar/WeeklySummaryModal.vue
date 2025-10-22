<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUiStore } from '@/stores/uiStore';
import { useTradesStore } from '@/stores/trades';
import { useNotebookStore } from '@/stores/notebookStore';
import { usePnlFormatting } from '@/composables/usePnlFormatting';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import IconButton from '@/components/ui/IconButton.vue';
import SparkleIcon from '@/components/icons/SparkleIcon.vue';
import DailyPnlChart from '../charts/DailyPnlChart.vue';
import BasePill from '@/components/ui/BasePill.vue';
import BaseTable from '@/components/ui/BaseTable.vue';

const uiStore = useUiStore();
const tradesStore = useTradesStore();
const notebookStore = useNotebookStore();
const router = useRouter();
const { pnlStyle, formatPnl } = usePnlFormatting();

const summaryData = computed(() => tradesStore.activeSummary);
const isLoading = computed(() => tradesStore.isSummaryLoading);

const handleClose = () => {
  uiStore.closeWeeklySummaryModal();
};

const handleAddWeeklyNote = async () => {
  if (!summaryData.value || !summaryData.value.startDate) return;

  if (notebookStore.folders.length === 0) await notebookStore.fetchFolders();

  const weeklyNotesFolder = notebookStore.folders.find(f => f.name === 'Weekly Notes');
  if (!weeklyNotesFolder) {
    console.error("Weekly Notes folder not found.");
    return;
  }

  const noteTitle = `Journal - ${formattedDateRange.value}`;
  let noteToEdit = weeklyNotesFolder.notes.find(n => n.title === noteTitle);

  if (!noteToEdit) {
    // createNote now returns the created note.
    noteToEdit = await notebookStore.createNote({
      folder_id: weeklyNotesFolder.id,
      title: noteTitle,
      content: { type: 'doc', content: [{ type: 'paragraph' }] }
    });
  }

  if (noteToEdit) {
    notebookStore.selectFolder(weeklyNotesFolder.id);
    notebookStore.selectNote(noteToEdit.id);
    router.push({ name: 'notebook' });
    handleClose();
  }
};

const formattedDateRange = computed(() => {
  if (!summaryData.value || !summaryData.value.startDate || !summaryData.value.endDate) return '';
  const start = new Date(summaryData.value.startDate);
  const end = new Date(summaryData.value.endDate);
  const startMonth = start.toLocaleDateString('en-US', { month: 'short' });
  const endMonth = end.toLocaleDateString('en-US', { month: 'short' });

  if (startMonth === endMonth) {
    return `${startMonth} ${start.getDate()} - ${end.getDate()}, ${start.getFullYear()}`;
  } else {
    return `${startMonth} ${start.getDate()} - ${endMonth} ${end.getDate()}, ${start.getFullYear()}`;
  }
});

const statsGrid = computed(() => {
    if (!summaryData.value || !summaryData.value.stats) return null;
    const stats = summaryData.value.stats;
    return {
        col1: [ { label: 'Total Trades', value: stats.trade_count }, { label: 'Winrate', value: `${stats.win_rate.toFixed(1)}%` } ],
        col2: [ { label: 'Winners', value: stats.winning_trades }, { label: 'Losers', value: stats.losing_trades }, ],
        col3: [
          { label: 'Gross Profit', value: formatPnl(stats.gross_profit), rawValue: stats.gross_profit, isPnl: true },
          { label: 'Gross Loss', value: formatPnl(stats.gross_loss, true), rawValue: stats.gross_loss, isPnl: true, isLoss: true },
        ],
        col4: [ { label: 'Net P&L', value: formatPnl(stats.net_pnl), rawValue: stats.net_pnl, isPnl: true }, { label: 'Profit Factor', value: stats.profit_factor_label } ]
    };
});

const tradeTableHeaders = computed(() => [
    { key: 'dayOfWeek', text: 'Day' },
    { key: 'entry_timestamp', text: 'Open Time' },
    { key: 'duration_minutes', text: 'Duration' },
    { key: 'symbol_snapshot', text: 'Symbol' },
    { key: 'direction', text: 'Side' },
    { key: 'setup', text: 'Playbook' },
    { key: 'p_l', text: 'Net P&L' },
]);

const formatDuration = (minutes) => {
  if (minutes === null || minutes === undefined) return '-';
  const mins = Math.floor(minutes);
  const secs = Math.round((minutes - mins) * 60);
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
};
</script>

<template>
  <BaseModal
    :show="uiStore.isWeeklySummaryModalOpen"
    @close="handleClose"
    :show-close-button="false"
    class="weekly-summary-modal"
  >
    <template #header>
      <div v-if="summaryData && summaryData.stats && !isLoading" class="header-content">
        <div class="header-left">
          <div class="header-info">
            <span class="date">{{ formattedDateRange }}</span>
            <span :style="pnlStyle(summaryData.stats.net_pnl)">Net P&L {{ formatPnl(summaryData.stats.net_pnl) }}</span>
          </div>
          <BaseButton variant="secondary" size="small" @click="handleAddWeeklyNote">Add Note</BaseButton>
        </div>
        <div class="header-right">
          <IconButton aria-label="AI Assistant" size="small"><SparkleIcon /></IconButton>
        </div>
      </div>
      <div v-else class="header-content">
        <h3>Loading Summary...</h3>
      </div>
    </template>

    <template #default>
      <div v-if="isLoading" class="loading-state">Loading data...</div>
      <div v-else-if="summaryData && summaryData.stats" class="modal-body-content">
        <div class="top-section">
          <div class="chart-section"><DailyPnlChart :chart-data="summaryData.cumulativePnlForChart" /></div>
          <div class="stats-section">
            <div class="stat-col" v-for="col in statsGrid" :key="col[0].label">
                <div v-for="stat in col" :key="stat.label" class="stat-cell">
                    <span class="stat-label">{{ stat.label }}</span>
                    <span v-if="stat.isPnl" class="stat-value" :style="pnlStyle(stat.rawValue, stat.isLoss)">{{ stat.value }}</span>
                    <span v-else class="stat-value">{{ stat.value }}</span>
                </div>
            </div>
          </div>
        </div>

        <div class="table-wrapper">
          <BaseTable :headers="tradeTableHeaders" :items="summaryData.trades" size="x-small">
            <template #p_l="{ item }">
              <span :style="pnlStyle(item.p_l)">{{ formatPnl(item.p_l) }}</span>
            </template>
            <template #setup="{ item }">
              <BasePill v-if="item.setup">{{ item.setup }}</BasePill>
            </template>
            <template #entry_timestamp="{ item }">
              {{ new Date(item.entry_timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) }}
            </template>
            <template #duration_minutes="{ item }">
              {{ formatDuration(item.duration_minutes) }}
            </template>
            <template #dayOfWeek="{ item }">
              {{ new Date(item.entry_timestamp).toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase() }}
            </template>
          </BaseTable>
        </div>
      </div>
      <div v-else-if="summaryData && summaryData.error" class="loading-state">
        <p>Error loading summary:</p>
        <p>{{ summaryData.error }}</p>
      </div>
      <div v-else class="loading-state">No trades for this week.</div>
    </template>

    <template #footer>
      <div class="footer-content">
        <BaseButton variant="secondary" size="small" @click="handleClose">Cancel</BaseButton>
        <BaseButton variant="primary" size="small">View Details</BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<style lang="scss" scoped>
/* --- Mobile First Styles --- */

/* Header Styles */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-sm);
}
.header-left {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}
.header-info {
  display: flex;
  flex-direction: column;
}
.date {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}
.header-info > span:last-child {
  font: var(--semantic-font-style-heading-sm);
  font-weight: 600;
}
.header-right {
  display: flex;
  align-items: center;
  gap: var(--base-size-spacing-2);
  flex-shrink: 0;
}

/* Body Styles */
.modal-body-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
  flex-grow: 1;
  min-height: 0;
}
.top-section {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}
.chart-section {
  min-height: 150px;
}

/* Stats Section Styles */
.stats-section {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 2 columns for mobile */
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  overflow: hidden;
}
.stat-col {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
  padding: var(--semantic-size-inset-sm);
}
/* Add borders to create a grid visually */
.stat-col:nth-child(odd) {
  border-right: var(--base-border-width-1) solid var(--semantic-color-border-default);
}
.stat-col:nth-child(1),
.stat-col:nth-child(2) {
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-default);
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
.loading-state {
  text-align: center;
  padding: var(--semantic-size-inset-xl);
  color: var(--semantic-color-text-secondary);
}

/* Table Styles */
.table-wrapper {
  flex-grow: 1;
  min-height: 0; /* Important for vertical scrolling in flex */
}

/* Footer Styles */
.footer-content {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-gap-sm);
  padding-top: var(--semantic-size-inset-md);
  border-top: var(--base-border-width-1) solid var(--semantic-color-border-default);
}

/* --- Tablet & Desktop Overrides --- */
@include media-up('md') {
  .modal-body-content {
    gap: var(--semantic-size-stack-lg);
  }
  .top-section {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    gap: var(--semantic-size-stack-xl);
    flex-direction: row; /* Revert to row for grid */
  }
  .stats-section {
    grid-template-columns: repeat(4, 1fr);
    border-left: var(--base-border-width-1) solid var(--semantic-color-border-default);
    border-top: none;
    border-right: none;
    border-bottom: none;
    border-radius: 0;
  }
  .stat-col {
    gap: var(--semantic-size-stack-lg);
    padding: 0 var(--semantic-size-inset-lg);
    border-right: var(--base-border-width-1) solid var(--semantic-color-border-default);
    border-bottom: none;
  }
  .stat-col:nth-child(odd) {
    border-right: var(--base-border-width-1) solid var(--semantic-color-border-default);
  }
  .stat-col:last-child {
    border-right: none;
  }
  .stat-col:nth-child(1),
  .stat-col:nth-child(2) {
    border-bottom: none;
  }
  .table-wrapper {
    min-width: 0; /* Fix for horizontal scrolling in flex */
    overflow-x: auto;
  }
}
</style>
