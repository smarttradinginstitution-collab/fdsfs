<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '@/services/api';
import { useUiStore } from '@/stores/uiStore';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import BaseTable from '@/components/ui/BaseTable.vue';
import UiCard from '@/components/ui/UiCard.vue';

const route = useRoute();
const uiStore = useUiStore();

const accountId = computed(() => route.params.account_id);
const isLoading = ref(true);
const holdings = ref({
  positions: [],
  balances: [],
  orders: []
});

const summaryByCurrency = computed(() => {
  const summary = {};

  // Process positions
  if (holdings.value.positions) {
    holdings.value.positions.forEach(pos => {
      const currency = pos.currency || 'UNKNOWN';
      if (!summary[currency]) {
        summary[currency] = { value: 0 };
      }
      summary[currency].value += (pos.units || 0) * (pos.price || 0);
    });
  }

  // Process balances
  if (holdings.value.balances) {
    holdings.value.balances.forEach(bal => {
      const currency = bal.currency_code || 'UNKNOWN';
      if (!summary[currency]) {
        summary[currency] = { value: 0 };
      }
      summary[currency].value += bal.cash_amount || 0;
    });
  }

  return summary;
});

const positionsHeaders = [
  { key: 'symbol', text: 'Symbol' },
  { key: 'description', text: 'Name' },
  { key: 'units', text: 'Units' },
  { key: 'average_purchase_price', text: 'Avg. Price' },
  { key: 'price', text: 'Current Price' },
  { key: 'market_value', text: 'Market Value' },
  { key: 'open_pnl', text: 'Unrealized P/L' },
];

const ordersHeaders = [
  { key: 'time_placed', text: 'Date' },
  { key: 'symbol', text: 'Symbol' },
  { key: 'action', text: 'Type' },
  { key: 'total_quantity', text: 'Quantity' },
  { key: 'execution_price', text: 'Price' },
  { key: 'status', text: 'Status' },
];

function formatCurrency(value, currency) {
  if (typeof value !== 'number') return '';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
  }).format(value);
}

function formatDate(dateString) {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString();
}

onMounted(async () => {
  if (!accountId.value) {
    uiStore.showNotification({ message: 'No account ID provided.', type: 'error' });
    isLoading.value = false;
    return;
  }

  try {
    const response = await apiClient.get(`/api/v1/accounts/${accountId.value}/holdings`);

    holdings.value = response.data;

    if (response.data.warning) {
      uiStore.showNotification({
        message: response.data.warning.message,
        type: 'warning',
        duration: 7000
      });
    }

  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'Failed to fetch account holdings.';
    uiStore.showNotification({ message: errorMessage, type: 'error' });
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div class="account-holdings-view">
    <header class="view-header">
      <h1>Account Details</h1>
      <p>Holdings, balances, and recent orders for account <span class="font-mono text-sm">{{ accountId }}</span>.</p>
    </header>

    <div v-if="isLoading" class="flex justify-center p-8">
      <LoadingSpinner />
    </div>

    <div v-else class="holdings-content grid-layout">

      <UiCard class="summary-card">
        <h2 class="card-title">Total Account Value</h2>
        <div v-if="Object.keys(summaryByCurrency).length > 0" class="summary-values">
          <div v-for="(summary, currency) in summaryByCurrency" :key="currency" class="summary-item">
            <span class="value">{{ formatCurrency(summary.value, currency) }}</span>
            <span class="currency">{{ currency }}</span>
          </div>
        </div>
        <div v-else class="text-secondary">
          No valuation data available.
        </div>
      </UiCard>

      <UiCard class="balances-card">
        <h2 class="card-title">Cash Balances</h2>
        <div v-if="holdings.balances && holdings.balances.length > 0" class="balance-values">
          <div v-for="balance in holdings.balances" :key="balance.currency_code" class="balance-item">
            <span>{{ formatCurrency(balance.cash_amount, balance.currency_code) }} <span class="currency"> (Cash)</span></span>
            <span>{{ formatCurrency(balance.buying_power, balance.currency_code) }} <span class="currency"> (Buying Power)</span></span>
          </div>
        </div>
        <div v-else class="text-secondary">
          No cash balance data available.
        </div>
      </UiCard>

      <section class="positions-section full-width">
        <h2 class="section-title">Positions</h2>
        <BaseTable v-if="holdings.positions && holdings.positions.length > 0" :headers="positionsHeaders" :items="holdings.positions">
          <template #symbol="{ item }">
            <span class="font-medium text-primary">{{ item.symbol }}</span>
          </template>
          <template #average_purchase_price="{ item }">
            {{ formatCurrency(item.average_purchase_price, item.currency) }}
          </template>
          <template #price="{ item }">
            {{ formatCurrency(item.price, item.currency) }}
          </template>
          <template #market_value="{ item }">
            <span class="font-medium">{{ formatCurrency(item.units * item.price, item.currency) }}</span>
          </template>
          <template #open_pnl="{ item }">
            <span :class="item.open_pnl >= 0 ? 'text-success' : 'text-danger'">
              {{ formatCurrency(item.open_pnl, item.currency) }}
            </span>
          </template>
        </BaseTable>
        <div v-else class="no-data-placeholder">
          No position data available.
        </div>
      </section>

      <section class="orders-section full-width">
        <h2 class="section-title">Recent Orders</h2>
        <BaseTable v-if="holdings.orders && holdings.orders.length > 0" :headers="ordersHeaders" :items="holdings.orders">
          <template #time_placed="{ item }">
            {{ formatDate(item.time_placed) }}
          </template>
           <template #execution_price="{ item }">
            {{ formatCurrency(item.execution_price, item.symbol?.currency?.code) }}
          </template>
        </BaseTable>
        <div v-else class="no-data-placeholder">
          No recent order data available.
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
.account-holdings-view {
  width: 100%;
  padding: var(--semantic-size-inset-xl);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.view-header {
  padding-bottom: var(--semantic-size-stack-lg);
  border-bottom: 1px solid var(--semantic-color-border-subtle);
}

.view-header h1 {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
}

.view-header p {
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
  margin-top: var(--semantic-size-stack-xs);
}

.placeholder {
  background-color: var(--semantic-color-bg-subtle);
  border: 1px solid var(--semantic-color-border-subtle);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--semantic-size-inset-lg);
  margin-top: var(--semantic-size-stack-md);
}
pre {
  white-space: pre-wrap;
  word-break: break-all;
  background-color: var(--semantic-color-bg-default);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-md);
}

.grid-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--semantic-size-gutter-lg);
}

.full-width {
  grid-column: 1 / -1;
}

.card-title {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-md);
}

.section-title {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-lg);
  padding-bottom: var(--semantic-size-stack-sm);
  border-bottom: 1px solid var(--semantic-color-border-subtle);
}

.summary-values, .balance-values {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}
.summary-item .value {
  font: var(--semantic-font-style-heading-md);
  color: var(--semantic-color-text-primary);
}
.summary-item .currency, .balance-item .currency {
  font-size: var(--semantic-font-size-sm);
  color: var(--semantic-color-text-subtle);
  margin-left: var(--semantic-size-inline-sm);
}
.balance-item {
  display: flex;
  justify-content: space-between;
}

.no-data-placeholder {
  background-color: var(--semantic-color-bg-subtle);
  border: 1px solid var(--semantic-color-border-subtle);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--semantic-size-inset-xl);
  text-align: center;
  color: var(--semantic-color-text-secondary);
}

.text-primary {
  color: var(--semantic-color-text-primary);
}
.text-secondary {
  color: var(--semantic-color-text-secondary);
}
.text-success {
  color: var(--semantic-color-text-success-default);
}
.text-danger {
  color: var(--semantic-color-text-danger-default);
}
.font-medium {
  font-weight: 500;
}
.font-mono {
  font-family: var(--semantic-font-family-mono);
}
.text-sm {
  font-size: var(--semantic-font-size-sm);
}

</style>
