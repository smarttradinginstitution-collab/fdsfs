<script setup>
import { computed } from 'vue';
import { useTradesStore } from '../../../../stores/trades';
import { useUiStore } from '../../../../stores/uiStore';
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

// 👇 Aggiunta: helper per disabilitare settimane future
function isFutureWeek(week) {
  const today = new Date();
  const weekDates = week.filter(d => !d.isPlaceholder).map(d => new Date(d.fullDate));
  if (weekDates.length === 0) return false;

  const firstDay = weekDates[0];
  return firstDay > today; // solo se tutta la settimana è dopo oggi
}


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

// --- CLICK HANDLERS ---
const handleDayClick = (day) => {
  if (day.isPlaceholder || day.dailyData.tradeCount === 0) return;
  const date = new Date(day.fullDate);
  // Usa la nuova azione specifica per il riepilogo
  tradesStore.fetchTradeSummary({ startDate: date, endDate: date });
  uiStore.openDailySummaryModal();
};

const handleWeekClick = (weekIndex) => {
  const week = calendarData.value.weeksOfDays[weekIndex];
  // 👇 Aggiunta: blocca settimane future
  if (isFutureWeek(week)) return;

  const weekDates = week.filter(day => !day.isPlaceholder).map(day => day.fullDate);
  if (weekDates.length > 0) {
    const startDate = new Date(weekDates[0]);
    const endDate = new Date(weekDates[weekDates.length - 1]);
    // Usa la nuova azione specifica per il riepilogo
    tradesStore.fetchTradeSummary({ startDate, endDate });
    uiStore.openWeeklySummaryModal();
  }
};
</script>

<template>
  <div class="calendar-card">
    <CalendarControls :month-label="controlsData.monthLabel" :monthly-pnl="controlsData.monthlyPnl" />
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
          <div v-if="!day.isPlaceholder" class="day-cell" :class="{ 'no-trade': day.dailyData.tradeCount === 0 }"
            :style="getPnlColor(day.dailyData.totalPnl)" @click="handleDayClick(day)">
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

        <!-- Riepilogo Settimanale - renderizzato una volta per riga della griglia -->
        <div v-if="uiStore.isWeeklySummaryVisible" class="week-summary-card" @click="handleWeekClick(weekIndex)"
          :class="{ disabled: isFutureWeek(week) }">
          <span class="week-title">Week {{ calendarData.weeklySummaries[weekIndex].weekNumber }}</span>
          <span class="week-pnl" :class="{
            'positive': calendarData.weeklySummaries[weekIndex].totalPnl > 0,
            'negative': calendarData.weeklySummaries[weekIndex].totalPnl < 0,
          }">
            {{ formatCellPnl(calendarData.weeklySummaries[weekIndex].totalPnl) }}
          </span>
          <span class="week-days">
            {{ calendarData.weeklySummaries[weekIndex].tradingDaysCount }}
            {{ calendarData.weeklySummaries[weekIndex].tradingDaysCount === 1 ? 'day' : 'days' }}
          </span>
        </div>
      </template>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.calendar-card {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding-block: var(--semantic-size-calendar-card-padding-block);
  padding-inline: var(--semantic-size-calendar-card-padding-inline);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  display: flex;
  flex-direction: column;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr) auto;
  gap: var(--semantic-size-calendar-grid-gap);
}

.day-header {
  text-align: center;
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-calendar-day-header);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--base-border-radius-sm);
  margin-bottom: var(--base-size-spacing-xs);
}

.week-summary-header {
  font-weight: var(--base-font-weight-bold);
}

.day-cell {
  position: relative;
  aspect-ratio: 1 / 1.5;
  border-radius: var(--base-border-radius-sm);
  padding: var(--semantic-size-calendar-day-cell-padding);
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
  font: var(--semantic-font-style-calendar-day-pnl);
  color: var(--semantic-color-text-secondary);
}

.day-trade-count,
.day-extra-stats {
  font: var(--semantic-font-style-calendar-day-details);
  color: var(--semantic-color-text-secondary);
}

.day-extra-stats {
  opacity: 0.8;
}

/* --- Stili per il riepilogo settimanale --- */
.week-summary-card {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: start;
  line-height: 1.15;
  gap: var(--base-size-spacing-1);
  padding: var(--semantic-size-inset-sm);
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--base-border-radius-sm);
  transition: all 150ms ease-in-out;
  cursor: pointer;
  /* L'altezza sarà determinata dalla griglia, allineandosi a aspect-ratio delle celle giorno */
}

.week-summary-card:hover {
  transform: scale(1.03);
  border-color: var(--semantic-color-border-focus);
  background-color: var(--semantic-color-surface-secondary);
}

/* 👇 Aggiunta: stato disabilitato per settimane future */
.week-summary-card.disabled {
  cursor: not-allowed;
  opacity: 0.5;
  pointer-events: none;
}

.week-title {
  font: var(--semantic-font-style-week-summary-label);
  color: var(--semantic-color-text-secondary);
  white-space: nowrap;
}

.week-days {
  font: var(--semantic-font-style-week-summary-label);
  color: var(--semantic-color-text-secondary);
  white-space: nowrap;
  /* Stili per lo sfondo richiesto */
  background-color: var(--semantic-color-surface-secondary);
  padding: 0.1rem var(--base-size-spacing-1-5);
  border-radius: var(--semantic-border-radius-tag);
}

.week-pnl {
  font: var(--semantic-font-style-week-summary-value);
  white-space: nowrap;
}

.week-pnl.positive {
  color: var(--semantic-color-feedback-positive-text);
}

.week-pnl.negative {
  color: var(--semantic-color-feedback-negative-text);
}

@include media-up('lg') {
  .day-extra-stats {
    display: block;
  }
}

@include media-down('lg') {
  .day-extra-stats {
    display: none;
  }
}

@include media-down('md') {
  .calendar-grid {
    grid-template-columns: repeat(7, 1fr);
  }

  .week-summary-header,
  .week-summary-card {
    /* Aggiornato da .week-summary-cell */
    display: none;
  }

  .day-details {
    line-height: 1.1;
  }
}

/* --- DARK THEME OVERRIDE --- */
/* The user requested that the text inside colored calendar cells be black for readability. */
[data-theme='dark'] .day-cell:not(.no-trade) .day-details,
[data-theme='dark'] .day-cell:not(.no-trade) .day-details span {
  color: #131316; /* Using a very dark gray from the palette for consistency */
}

[data-theme='dark'] .day-cell:not(.no-trade) .day-number {
  color: #131316;
  opacity: 0.6;
}
</style>
