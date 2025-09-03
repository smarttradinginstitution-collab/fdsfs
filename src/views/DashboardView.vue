<!--
// =============================================================================
// FILE: views/DashboardView.vue
// DESCRIZIONE: Vista della Dashboard, ora con i bottoni di azione principali
// posizionati in una loro sezione dedicata.
// =============================================================================
-->
<script setup>
import { ref, computed, onMounted } from 'vue';
import apiClient from '../services/api';
import StatCard from '../components/dashboard/StatCard.vue';
import CalendarHeatmap from '../components/dashboard/CalendarHeatmap.vue';
import RecentTradesTable from '../components/dashboard/RecentTradesTable.vue';
import BaseModal from '../components/ui/BaseModal.vue';
import NewTradeForm from '../components/trades/NewTradeForm.vue';
import StatSelector from '../components/dashboard/StatSelector.vue';
import BaseButton from '../components/ui/BaseButton.vue';
import SettingsIcon from '../components/icons/SettingsIcon.vue';
import PlusIcon from '../components/icons/PlusIcon.vue';
import { useTradesStore } from '../stores/trades';
import { useUiStore } from '../stores/uiStore';
import DailySummaryModal from '../components/dashboard/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/WeeklySummaryModal.vue';

const tradesStore = useTradesStore();
const uiStore = useUiStore();

const isAddTradeModalOpen = ref(false);
const isSettingsModalOpen = ref(false);

const handleNewTrade = (tradeData) => {
  tradesStore.addTrade(tradeData);
  isAddTradeModalOpen.value = false;
};

const visibleStats = computed(() => {
  const visibleKeys = uiStore.visibleStatKeys;
  const allStats = tradesStore.allDashboardStats;
  return visibleKeys.map(key => allStats[key]);
});

// --- DATA FETCHING EXAMPLE ---
// Esempio di come recuperare i dati dal backend
const backendData = ref(null);
const fetchError = ref(null);

onMounted(async () => {
  try {
    // Replace '/api/v1/trades' with your actual endpoint.
    // Sostituisci '/api/v1/trades' con il tuo vero endpoint.
    const response = await apiClient.get('/api/v1/trades');
    backendData.value = response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
    fetchError.value = 'Failed to fetch data from the backend. Make sure the backend is running and that the VITE_API_URL in your .env file is correct.';
    // Also, check the browser's console for CORS errors.
    // Controlla anche la console del browser per errori CORS.
  }
});
</script>

<template>
  <div class="dashboard-view">

    <!-- Esempio di visualizzazione dati dal backend -->
    <div v-if="fetchError" class="error-box">
      <h3>Backend Connection Error</h3>
      <p>{{ fetchError }}</p>
    </div>
    <div v-if="backendData" class="data-box">
      <h3>Data from Backend (for testing):</h3>
      <pre>{{ JSON.stringify(backendData, null, 2) }}</pre>
    </div>


    <div class="action-bar">
      <BaseButton variant="secondary" @click="isSettingsModalOpen = true">
        <SettingsIcon />
        <span>Modifica Widget</span>
      </BaseButton>
      <BaseButton variant="primary" @click="isAddTradeModalOpen = true">
        <PlusIcon />
        <span>Nuovo Trade</span>
      </BaseButton>
    </div>

    <div class="stats-grid">
      <StatCard
        v-for="stat in visibleStats"
        :key="stat.key"
        :stat="stat"
      />
    </div>

    <div class="main-content-grid">
      <CalendarHeatmap />
      <RecentTradesTable />
    </div>

    <!-- Modale per Aggiungere un Trade -->
    <BaseModal :show="isAddTradeModalOpen" @close="isAddTradeModalOpen = false">
      <template #header><h3>Log New Trade</h3></template>
      <NewTradeForm @submit="handleNewTrade" />
    </BaseModal>

    <!-- Modale per Personalizzare le Statistiche -->
    <BaseModal :show="isSettingsModalOpen" @close="isSettingsModalOpen = false">
      <template #header><h3>Customize Dashboard Stats</h3></template>
      <template #default><StatSelector /></template>
    </BaseModal>

    <!-- Modale per il Riepilogo Giornaliero -->
    <DailySummaryModal />
    <!-- Modale per il Riepilogo Settimanale -->
    <WeeklySummaryModal />
  </div>
</template>

<style scoped>
/*
// =============================================================================
// STYLING: views/DashboardView.vue
// DESCRIZIONE: Aggiunta di stili iper-responsive.
//
// NOTE:
// - Usiamo clamp() per rendere le spaziature fluide. I valori min/max sono
//   basati sui token esistenti per mantenere coerenza.
// - Aggiunte media query per breakpoint più piccoli per riorganizzare i layout
//   in modo significativo (es. stacking di elementi).
// =============================================================================
*/
.dashboard-view {
  width: 100%;
  /* Spaziatura fluida per il padding principale */
  padding: clamp(var(--semantic-size-inset-md), 4vw, var(--semantic-size-inset-xl));
  display: flex;
  flex-direction: column;
  /* Spaziatura fluida tra le sezioni */
  gap: clamp(var(--semantic-size-stack-md), 5vh, var(--semantic-size-stack-lg));
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
  flex-wrap: wrap; /* Permette ai bottoni di andare a capo su schermi piccoli */
}

.stats-grid {
  display: grid;
  /* La funzione minmax() è già ottima per la responsività delle card */
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  /* Spaziatura fluida tra le card */
  gap: clamp(var(--semantic-size-stack-sm), 3vw, var(--semantic-size-stack-md));
}

.main-content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  /* Spaziatura fluida tra i widget principali */
  gap: clamp(var(--semantic-size-stack-md), 5vh, var(--semantic-size-stack-lg));
  grid-auto-flow: dense;
}

.main-content-grid > * {
  min-width: 0;
}

.error-box, .data-box {
  padding: var(--semantic-size-inset-lg);
  border-radius: var(--semantic-border-radius-lg);
  background-color: var(--color-background-muted);
  border: 1px solid var(--color-border-subtle);
}

.error-box {
  background-color: var(--color-background-negative-subtle);
  border-color: var(--color-border-negative);
  color: var(--color-text-negative);
}

.data-box pre {
  white-space: pre-wrap;
  word-break: break-all;
  background-color: var(--color-background-subtle);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-md);
}

/* --- Media Queries per Iper-Responsività --- */

/* Tablet e schermi medi (es. iPad in verticale) */
@media (max-width: 1024px) {
  .main-content-grid {
    /* Passa a una singola colonna prima */
    grid-template-columns: 1fr;
  }

  .stats-grid {
    /* Aumenta la dimensione minima delle card per evitare che diventino troppo piccole */
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
}

/* Cellulari grandi (es. tablet in verticale, cellulari in orizzontale) */
@media (max-width: 768px) {
  .action-bar {
    /* I bottoni ora occupano tutta la larghezza e sono giustificati allo stesso modo */
    justify-content: space-between;
  }

  .action-bar > * {
    /* Assicura che i bottoni abbiano una larghezza minima e possano crescere */
    flex-grow: 1;
    min-width: 150px;
  }
}

/* Cellulari piccoli */
@media (max-width: 480px) {
  .dashboard-view {
    /* Riduci ulteriormente il padding su schermi molto piccoli */
    padding: clamp(var(--base-size-spacing-2), 3vw, var(--semantic-size-inset-md));
  }

  .action-bar {
    flex-direction: column; /* Impila i bottoni verticalmente */
    align-items: stretch; /* Allunga i bottoni a tutta larghezza */
  }
}
</style>
