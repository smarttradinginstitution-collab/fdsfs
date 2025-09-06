<script setup>
import { computed } from 'vue';
import { useTradesStore } from '../../stores/trades';
import { useUiStore } from '../../stores/uiStore';
import CalendarControls from './CalendarControls.vue';

const tradesStore = useTradesStore();
const uiStore = useUiStore();

// Dati per il corpo del calendario (heatmap)
const calendarData = computed(() => tradesStore.calendarDataByMonth);
// Dati per l'header con i controlli
const controlsData = computed(() => tradesStore.calendarControlsData);

const gridStyle = computed(() => ({
  gridTemplateColumns: uiStore.isWeeklySummaryVisible
    ? 'repeat(7, 1fr) auto'
    : 'repeat(7, 1fr)',
}));

// Funzione helper per il colore di sfondo
function getPnlColor(pnl) {
  if (pnl === 0) return {};
  const opacity = Math.min(Math.abs(pnl) / 500, 0.9) + 0.1;
  if (pnl > 0) return { backgroundColor: `rgba(22, 163, 74, ${opacity})` };
  return { backgroundColor: `rgba(220, 38, 38, ${opacity})` };
}

// Funzione helper per formattare il P&L nelle celle
function formatCellPnl(pnl) {
  if (pnl === 0) return '$0';
  const sign = pnl > 0 ? '' : '-';
  const num = Math.abs(pnl);

  if (num < 1000) return `${sign}$${num.toFixed(0)}`;
  if (num >= 1000 && num < 1000000) return `${sign}${(num / 1000).toFixed(1).replace(/\.0$/, '')}k`;
  return `${sign}${(num / 1000000).toFixed(1).replace(/\.0$/, '')}M`;
}
</script>

<template>
  <div class="calendar-card">
    <CalendarControls
      :month-label="controlsData.monthLabel"
      :monthly-pnl="controlsData.monthlyPnl"
    />
    <div class="calendar-grid" :style="gridStyle">
      <div class="day-header">Mon</div>
      <div class="day-header">Tue</div>
      <div class="day-header">Wed</div>
      <div class="day-header">Thu</div>
      <div class="day-header">Fri</div>
      <div class="day-header">Sat</div>
      <div class="day-header">Sun</div>
      <div v-if="uiStore.isWeeklySummaryVisible" class="week-summary-header"></div>

      <template v-for="(week, weekIndex) in calendarData.weeksOfDays" :key="`week-${weekIndex}`">
        <!-- Loop per i giorni di ogni settimana -->
        <template v-for="day in week" :key="day.key">
          <div
            v-if="!day.isPlaceholder"
            class="day-cell"
            :class="{ 'no-trade': day.dailyData.tradeCount === 0 }"
            :style="getPnlColor(day.dailyData.totalPnl)"
            @click="uiStore.openDailySummaryModal(day.fullDate)"
          >
            <span class="day-number">{{ day.date }}</span>
            <div v-if="day.dailyData.tradeCount > 0" class="day-details">
              <span class="day-pnl" :class="day.dailyData.totalPnl >= 0 ? 'positive' : 'negative'">
                {{ formatCellPnl(day.dailyData.totalPnl) }}
              </span>
            <span v-if="uiStore.isCalendarTradeCountVisible" class="day-trade-count">
                {{ day.dailyData.tradeCount }} {{ day.dailyData.tradeCount === 1 ? 'trade' : 'trades' }}
              </span>
            <span v-if="uiStore.isCalendarWinRateVisible" class="day-extra-stats">
                {{ ((day.dailyData.winningTrades / day.dailyData.tradeCount) * 100).toFixed(0) }}% WR
              </span>
            </div>
          </div>
          <div v-else class="day-cell placeholder"></div>
        </template>

        <!-- Riepilogo Settimanale - Clonato dalla struttura di .day-cell per coerenza -->
        <div
          v-if="uiStore.isWeeklySummaryVisible"
          class="day-cell week-summary-card"
          @click="uiStore.openWeeklySummaryModal(weekIndex)"
        >
          <span class="day-number">W{{ calendarData.weeklySummaries[weekIndex].weekNumber }}</span>
          <div class="day-details">
            <span class="day-pnl" :class="{
                'positive': calendarData.weeklySummaries[weekIndex].totalPnl > 0,
                'negative': calendarData.weeklySummaries[weekIndex].totalPnl < 0,
              }">
              {{ formatCellPnl(calendarData.weeklySummaries[weekIndex].totalPnl) }}
            </span>
            <span class="day-trade-count">
              {{ calendarData.weeklySummaries[weekIndex].tradingDaysCount }}
              {{ calendarData.weeklySummaries[weekIndex].tradingDaysCount === 1 ? 'day' : 'days' }}
            </span>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.calendar-card {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding-block: var(--semantic-size-calendar-card-padding-block-mobile);
  padding-inline: var(--semantic-size-calendar-card-padding-inline-mobile);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  display: flex;
  flex-direction: column;
}
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr) auto;
  gap: var(--semantic-size-calendar-grid-gap-mobile);
}
.day-header {
  text-align: center;
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-calendar-day-header);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--base-border-radius-sm);
  margin-bottom: var(--semantic-size-stack-xs);
}
.week-summary-header {
  /* This class is empty and unused. */
}
.day-cell {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-calendar-day-cell-padding-mobile);
  transition: transform 150ms;
  display: flex;
  align-items: center;
  cursor: pointer;
  justify-content: center;
  overflow: hidden;
}
.day-cell:not(.placeholder):hover {
    transform: scale(1.05);
    outline: 2px solid var(--semantic-color-border-focus);
}
.placeholder {
  background-color: transparent;
}
.no-trade {
  background-color: var(--semantic-color-surface-secondary);
}
.day-number {
  position: absolute;
  top: 0.1rem;
  right: 0.35rem;
  font: var(--semantic-font-style-calendar-day-number);
  color: var(--semantic-color-text-secondary);
}
.day-cell:not(.no-trade) .day-number {
  color: var(--semantic-color-text-secondary);
  opacity: 0.7;
}
.day-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0;
  line-height: 1.15;
  color: var(--semantic-color-text-on-brand);
  width: 100%;
}
.day-pnl {
  font: var(--semantic-font-style-data-display-lg-bold);
  color: var(--semantic-color-text-secondary);
}
.day-trade-count {
  font: var(--semantic-font-style-label-xxs);
  color: var(--semantic-color-text-secondary);
}
.day-extra-stats {
  font: var(--semantic-font-style-label-xxs);
  color: var(--semantic-color-text-secondary);
  opacity: 0.8;
}
/* --- Stili per il riepilogo settimanale --- */
/* Questa ora è una classe modificatrice. Applica solo gli stili che
   differiscono da .day-cell */
.week-summary-card {
  background-color: var(--semantic-color-surface-primary);
  /* Sovrascrive il colore di sfondo del PNL da .day-cell */
}

/* Allineiamo i dettagli a sinistra, a differenza di .day-details che li allinea a destra */
.week-summary-card .day-details {
  align-items: flex-start;
}

/* Il pnl settimanale non deve ereditare il colore grigio da .day-pnl */
.week-summary-card .day-pnl {
  color: inherit;
}

.week-summary-card .day-pnl.positive {
  color: var(--semantic-color-feedback-positive-text);
}

.week-summary-card .day-pnl.negative {
  color: var(--semantic-color-feedback-negative-text);
}

.week-summary-card:hover {
  transform: scale(1.03);
  border-color: var(--semantic-color-border-focus);
  background-color: var(--semantic-color-surface-secondary);
}

@media (min-width: 768px) {
  .calendar-card {
    padding-block: var(--semantic-size-calendar-card-padding-block-tablet);
    padding-inline: var(--semantic-size-calendar-card-padding-inline-tablet);
  }
  .calendar-grid {
    gap: var(--semantic-size-calendar-grid-gap-tablet);
  }
  .day-cell {
    padding: var(--semantic-size-calendar-day-cell-padding-tablet);
  }
}

@media (min-width: 1024px) {
  .calendar-card {
    padding-block: var(--semantic-size-calendar-card-padding-block-desktop);
    padding-inline: var(--semantic-size-calendar-card-padding-inline-desktop);
  }
  .calendar-grid {
    gap: var(--semantic-size-calendar-grid-gap-desktop);
  }
  .day-cell {
    padding: var(--semantic-size-calendar-day-cell-padding-desktop);
  }
  .day-extra-stats {
    display: block;
  }
}

@media (max-width: 1024px) {
  .day-extra-stats { display: none; }
}

@media (max-width: 768px) {
    .calendar-grid {
      grid-template-columns: repeat(7, 1fr);
    }
    .week-summary-header,
    .week-summary-card { /* Aggiornato da .week-summary-cell */
      display: none;
    }
    .day-details {
        line-height: 1.1;
    }
}
</style>
