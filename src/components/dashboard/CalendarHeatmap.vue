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

        <!-- Riepilogo Settimanale - renderizzato una volta per riga della griglia -->
        <div
          v-if="uiStore.isWeeklySummaryVisible"
          class="week-summary-card"
          @click="uiStore.openWeeklySummaryModal(weekIndex)"
        >
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

<style scoped>
/*
// =============================================================================
// STYLING: components/dashboard/CalendarHeatmap.vue
// DESCRIZIONE: Aggiunta di stili iper-responsive per il calendario.
//
// NOTE:
// - Tipografia e spaziature rese fluide.
// - Media query aggiuntive per gestire la visibilità degli elementi
//   su schermi molto piccoli, garantendo leggibilità.
// =============================================================================
*/
.calendar-card {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  /* Padding fluido */
  padding: clamp(var(--semantic-size-inset-sm), 3vw, var(--semantic-size-inset-lg));
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}
.calendar-grid {
  display: grid;
  /* Il numero di colonne è gestito dinamicamente via :style */
  gap: clamp(2px, 1vw, var(--base-size-spacing-1));
}
.day-header {
  text-align: center;
  color: var(--semantic-color-text-secondary);
  font-size: clamp(0.6rem, 2vw, 0.8rem);
  font-weight: var(--base-font-weight-medium);
  padding: var(--base-size-spacing-1);
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-subtle);
  margin-bottom: var(--base-size-spacing-xs);
}
.week-summary-header {
  font-weight: var(--base-font-weight-bold);
}
.day-cell {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: var(--base-border-radius-sm);
  padding: clamp(2px, 0.6vw, 4px);
  transition: transform 150ms;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  justify-content: center;
  overflow: hidden;
  text-align: center;
}
.day-cell:not(.placeholder):hover {
    transform: scale(1.05);
    outline: 2px solid var(--semantic-color-border-focus);
    z-index: var(--base-layer-z-index-above);
}
.placeholder {
  background-color: transparent;
}
.no-trade {
  background-color: var(--semantic-color-surface-secondary);
}
.day-number {
  position: absolute;
  top: clamp(1px, 0.5vw, 3px);
  right: clamp(2px, 0.8vw, 5px);
  font-size: clamp(0.6rem, 1.8vw, 0.7rem);
  color: var(--semantic-color-text-tertiary);
}
.day-cell:not(.no-trade) .day-number {
  opacity: 0.7;
}
.day-details {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0;
  line-height: 1.1;
  color: var(--semantic-color-text-on-brand);
  width: 100%;
  height: 100%;
}
.day-pnl {
  font-weight: var(--base-font-weight-bold);
  color: var(--semantic-color-text-on-brand); /* Colore unificato per contrasto */
  font-size: clamp(0.7rem, 2.5vw, 1.1rem);
}
.day-pnl.negative {
  /* Usiamo lo stesso colore per il testo, il bg indica già la direzione */
}
.day-trade-count, .day-extra-stats {
  font-size: clamp(0.5rem, 1.5vw, 0.65rem);
  color: var(--semantic-color-text-on-brand);
  opacity: 0.8;
}

/* --- Stili per il riepilogo settimanale --- */
.week-summary-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  line-height: 1.2;
  gap: clamp(2px, 0.5vw, 4px);
  padding: clamp(4px, 1vw, var(--semantic-size-inset-sm));
  background-color: var(--semantic-color-surface-primary);
  border-left: var(--base-border-width-1) solid var(--semantic-color-border-default);
  transition: all 150ms ease-in-out;
  cursor: pointer;
}
.week-summary-card:hover {
  background-color: var(--semantic-color-surface-secondary);
}

.week-title {
  font-size: clamp(0.6rem, 1.8vw, 0.7rem);
  color: var(--semantic-color-text-secondary);
  white-space: nowrap;
}

.week-days {
  font-size: clamp(0.6rem, 1.8vw, 0.7rem);
  color: var(--semantic-color-text-secondary);
  white-space: nowrap;
  background-color: var(--semantic-color-surface-secondary);
  padding: 0.1rem var(--base-size-spacing-1-5);
  border-radius: var(--semantic-border-radius-tag);
}

.week-pnl {
  font-size: clamp(0.7rem, 2.2vw, 0.85rem);
  font-family: var(--semantic-font-style-data-numeric-font-family);
  font-weight: var(--base-font-weight-semibold);
  white-space: nowrap;
}

.week-pnl.positive {
  color: var(--semantic-color-feedback-positive-text);
}

.week-pnl.negative {
  color: var(--semantic-color-feedback-negative-text);
}

/* --- Media Queries per Iper-Responsività --- */

@media (max-width: 1024px) {
  .day-extra-stats { display: none; }
}

@media (max-width: 768px) {
    .calendar-grid {
      /* Rimuove la colonna del riepilogo settimanale */
      grid-template-columns: repeat(7, 1fr);
    }
    .week-summary-header,
    .week-summary-card {
      display: none;
    }
    .day-details {
        line-height: 1; /* Più compatto */
    }
}

@media (max-width: 480px) {
  .day-trade-count {
    /* Nasconde il numero di trade su schermi molto piccoli per non affollare */
    display: none;
  }
  .day-pnl {
    /* Riduciamo leggermente il P&L per fare spazio */
    font-size: clamp(0.65rem, 3vw, 0.9rem);
  }
}

@media (max-width: 320px) {
  .day-header {
    /* Abbreviamo i giorni della settimana su schermi piccolissimi */
    font-size: 0.6rem;
  }
  .calendar-card {
    padding: var(--semantic-size-inset-sm);
  }
}
</style>
