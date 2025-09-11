<script setup>
import { computed } from 'vue';
import { useTradesStore } from '../../stores/trades';
import { useUiStore } from '../../stores/uiStore';
import CalendarControls from './CalendarControls.vue';

const tradesStore = useTradesStore();
const uiStore = useUiStore();

// Dati per il corpo del calendario (heatmap)
const calendarData = computed(() => tradesStore.calendarDataByMonth);
// Dati per i controlli del calendario (es. mese, pnl mensile)
const controlsData = computed(() => tradesStore.calendarControlsData);
// Dati per il footer
const footerData = computed(() => tradesStore.progressTrackerFooterData);

const gridStyle = computed(() => ({
  gridTemplateColumns: uiStore.isWeeklySummaryVisible
    ? 'repeat(7, 1fr) auto'
    : 'repeat(7, 1fr)',
}));

const circularProgressStyle = computed(() => {
  const score = footerData.value.todayScore;
  const percentage = (score.current / score.max) * 100;
  // Usiamo un conic-gradient per creare l'effetto di progresso circolare
  return {
    background: `radial-gradient(white 60%, transparent 61%), conic-gradient(var(--color-background-positive-strong) ${percentage}%, var(--color-background-interactive-secondary-disabled) 0)`,
  };
});

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
  <div class="card">
    <div class="card-header">
      <h3 class="widget-title">Progress tracker</h3>
      <div>
        <span class="view-more-link">View more</span>
      </div>
    </div>

    <div class="calendar-content">
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

    <div class="card-footer">
      <div class="footer-left">
        <div class="circular-progress" :style="circularProgressStyle">
          <span class="progress-text">{{ footerData.todayScore.current }}/{{ footerData.todayScore.max }}</span>
        </div>
        <span class="footer-title">Today's score</span>
      </div>
      <a href="#" class="daily-checklist-link">Daily checklist</a>
    </div>
  </div>
</template>

<style scoped>
/* Stili generali della card, presi dagli altri widget per coerenza */
.card {
  background-color: var(--color-background-card-primary);
  border: 1px solid var(--color-border-card-primary);
  border-radius: var(--semantic-border-radius-lg);
  box-shadow: var(--effect-shadow-small);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
  color: var(--color-text-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.widget-title {
  font: var(--typography-style-heading-h5);
}

.card-header > div {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

.view-more-link {
  font: var(--typography-style-link-small);
  color: var(--color-text-interactive-primary-strong);
  cursor: pointer;
}

.calendar-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
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
  margin-bottom: var(--base-size-spacing-xs);
}

.week-summary-header {
  font-weight: var(--base-font-weight-bold);
}

.day-cell {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: var(--base-border-radius-sm);
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
  font-weight: var(--base-font-weight-bold);
  color: var(--semantic-color-text-secondary);
  font-size: clamp(var(--base-font-fluid-size-lg-min),
      var(--base-font-fluid-size-lg-ideal),
      var(--base-font-fluid-size-lg-max));
}

.day-trade-count {
  color: var(--semantic-color-text-secondary);
  font-size: clamp(var(--base-font-fluid-size-xxs-min),
      var(--base-font-fluid-size-xxs-ideal),
      var(--base-font-fluid-size-xxs-max));
}

.day-extra-stats {
  color: var(--semantic-color-text-secondary);
  opacity: 0.8;
  font-size: clamp(var(--base-font-fluid-size-xxs-min),
      var(--base-font-fluid-size-xxs-ideal),
      var(--base-font-fluid-size-xxs-max));
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
  font-family: var(--base-font-family-palette-sans);
  font-size: 0.7rem;
  color: var(--semantic-color-text-secondary);
  line-height: 1.2;
  white-space: nowrap;
}

.week-days {
  font-family: var(--base-font-family-palette-sans);
  font-size: 0.7rem;
  color: var(--semantic-color-text-secondary);
  line-height: 1.2;
  white-space: nowrap;
  /* Stili per lo sfondo richiesto */
  background-color: var(--semantic-color-surface-secondary);
  padding: 0.1rem var(--base-size-spacing-1-5);
  border-radius: var(--semantic-border-radius-tag);
}

.week-pnl {
  font-size: var(--base-font-size-sm);
  font-family: var(--semantic-font-style-data-numeric-font-family);
  font-weight: var(--base-font-weight-semibold);
  line-height: 1.2;
  white-space: nowrap;
}

.week-pnl.positive {
  color: var(--semantic-color-feedback-positive-text);
}

.week-pnl.negative {
  color: var(--semantic-color-feedback-negative-text);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--color-border-subtle);
  padding-top: var(--semantic-size-stack-md);
}

.footer-left {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

.circular-progress {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.progress-text {
  font: var(--typography-style-label-small);
  color: var(--color-text-primary);
  z-index: 1;
}

.footer-title {
  font: var(--typography-style-body-medium);
  color: var(--color-text-secondary);
}

.daily-checklist-link {
  font: var(--typography-style-link-small);
  color: var(--color-text-interactive-primary-strong);
  text-decoration: none;
}


@media (min-width: 768px) {
  .card {
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
  .day-extra-stats {
    display: none;
  }
}

@media (max-width: 768px) {
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
</style>
