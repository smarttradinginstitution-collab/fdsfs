<!--
// =============================================================================
// FILE: views/TradesView.vue
// DESCRIZIONE: Questo componente rappresenta la "vista" della pagina "My Trades".
// Il suo unico scopo è mostrare una tabella con la lista completa di tutti
// i trade registrati dall'utente.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import { onMounted, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useTradesStore } from '@/stores/trades';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import { formatCurrency, formatNumber, formatPercentage } from '@/services/formatters';
import TradesStatCard from '@/components/dashboard/widgets/TradesStatCard.vue';
import BaseTable from '@/components/ui/BaseTable.vue';

// --- LOGICA DEL COMPONENTE ---
const tradesStore = useTradesStore();
const tradingAccountsStore = useTradingAccountsStore();

const { kpiDashboardData, trades } = storeToRefs(tradesStore);
const { selectedTradingAccount } = storeToRefs(tradingAccountsStore);

// --- DATA FETCHING ---
onMounted(() => {
  if (selectedTradingAccount.value) {
    tradesStore.fetchKpiDashboardData();
    tradesStore.fetchTrades();
  }
});

// --- COMPUTED PROPERTIES PER LE STATISTICHE ---
const kpiStats = computed(() => {
    if (!kpiDashboardData.value) {
        // Return a default structure to prevent rendering errors
        const defaultStat = { value: 'N/A', changeType: 'neutral', label: '' };
        return {
            netCumulativePnl: { ...defaultStat, key: 'netCumulativePnl', label: 'Net Cumulative P&L', series: [] },
            profitFactor: { ...defaultStat, key: 'profitFactor', label: 'Profit Factor' },
            winPercentage: { ...defaultStat, key: 'winPercentage', label: 'Win %', wins: 0, losses: 0 },
            avgWinLoss: { ...defaultStat, key: 'avgWinLoss', label: 'Avg Win/Loss', avgWin: 0, avgLoss: 0 },
        };
    }

    const data = kpiDashboardData.value;
    return {
        netCumulativePnl: {
            key: 'netCumulativePnl',
            label: 'Net Cumulative P&L',
            value: formatCurrency(data.netCumulativePnl.total),
            changeType: data.netCumulativePnl.total >= 0 ? 'positive' : 'negative',
            series: data.netCumulativePnl.series,
        },
        profitFactor: {
            key: 'profitFactor',
            label: 'Profit Factor',
            value: data.profitFactor ? formatNumber(data.profitFactor, 2) : '∞',
            changeType: 'neutral',
        },
        winPercentage: {
            key: 'winPercentage',
            label: 'Win %',
            value: formatPercentage(data.winPercentage),
            wins: data.winningTrades,
            losses: data.losingTrades,
            changeType: 'neutral',
        },
        avgWinLoss: {
            key: 'avgWinLoss',
            label: 'Avg Win/Loss Trade',
            value: 'N/A', // Questo valore non viene mostrato, il grafico mostra i dettagli
            avgWin: data.avgWin,
            avgLoss: data.avgLoss,
            changeType: 'neutral',
        },
    };
});
</script>

<template>
  <div class="trades-view">
    <div class="kpi-dashboard">
        <TradesStatCard :stat="kpiStats.netCumulativePnl" />
        <TradesStatCard :stat="kpiStats.profitFactor" />
        <TradesStatCard :stat="kpiStats.winPercentage" />
        <TradesStatCard :stat="kpiStats.avgWinLoss" />
    </div>
    <BaseTable
      :headers="tradesStore.tradeHeaders"
      :items="trades"
    />
  </div>
</template>

<style scoped>
.trades-view {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
  padding: var(--semantic-size-inset-xl);
  flex-grow: 1;
}

.kpi-dashboard {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--semantic-size-stack-md);
}

/* Responsive adjustments for smaller screens */
@media (max-width: 1200px) {
  .kpi-dashboard {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .kpi-dashboard {
    grid-template-columns: 1fr;
  }
}
</style>