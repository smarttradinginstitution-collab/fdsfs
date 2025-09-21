<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '@/services/api';
import { useUiStore } from '@/stores/uiStore';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import BaseTable from '@/components/ui/BaseTable.vue';

const route = useRoute();
const uiStore = useUiStore();

const holdings = ref(null);
const isLoading = ref(true);
const error = ref(null);

const accountId = computed(() => route.params.accountId);

const positionHeaders = [
  { key: 'symbol', text: 'Symbol' },
  { key: 'description', text: 'Description' },
  { key: 'units', text: 'Units' },
  { key: 'price', text: 'Market Price' },
  { key: 'marketValue', text: 'Market Value' },
  { key: 'open_pnl', text: 'Open P&L' },
];

const orderHeaders = [
  { key: 'symbol', text: 'Symbol' },
  { key: 'action', text: 'Action' },
  { key: 'status', text: 'Status' },
  { key: 'total_quantity', text: 'Quantity' },
  { key: 'limit_price', text: 'Limit Price' },
  { key: 'time_placed', text: 'Time Placed' },
];

const totalBalance = computed(() => {
  if (!holdings.value) return 0;
  const cashTotal = holdings.value.balances.reduce((sum, balance) => sum + (balance.cash_amount || 0), 0);
  const positionsTotal = holdings.value.positions.reduce((sum, pos) => sum + (pos.units * pos.price), 0);
  return cashTotal + positionsTotal;
});

const recentOrders = computed(() => {
  if (!holdings.value || !holdings.value.orders) return [];
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  return holdings.value.orders.filter(order => new Date(order.time_placed) > thirtyDaysAgo);
});

function formatCurrency(value, currency = 'USD') {
  if (typeof value !== 'number') return '';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(value);
}

function formatDate(dateString) {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString();
}

async function fetchHoldings() {
  if (!accountId.value) {
    error.value = 'No account ID provided in the URL.';
    isLoading.value = false;
    return;
  }

  try {
    isLoading.value = true;
    error.value = null;
    const response = await apiClient.get(`/api/v1/accounts/${accountId.value}/holdings`);
    holdings.value = response.data;
  } catch (err) {
    const errorMessage = err.response?.data?.detail || 'Failed to fetch account holdings.';
    error.value = errorMessage;
    uiStore.showNotification({ message: errorMessage, type: 'error' });
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

onMounted(fetchHoldings);
</script>

<template>
  <div class="account-holdings-view">
    <div v-if="isLoading" class="loading-state">
      <LoadingSpinner />
      <p>Loading account details...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <h2>Error</h2>
      <p>{{ error }}</p>
      <button @click="fetchHoldings">Try Again</button>
    </div>
    <div v-else-if="holdings" class="holdings-content">
      <header class="view-header">
        <h1>Account Dashboard</h1>
        <p>A complete overview of your trading account's holdings, balances, and recent orders.</p>
      </header>

      <!-- Summary Section -->
      <section class="summary-section">
        <div class="summary-card">
          <span class="label">Total Balance</span>
          <span class="value">{{ formatCurrency(totalBalance, holdings.balances[0]?.currency_code) }}</span>
        </div>
         <div class="summary-card">
          <span class="label">Account ID</span>
          <span class="value font-mono text-sm">{{ accountId }}</span>
        </div>
      </section>

      <!-- Positions Section -->
      <section>
        <h2>Positions</h2>
        <BaseTable :headers="positionHeaders" :items="holdings.positions">
          <template #price="{ item }">{{ formatCurrency(item.price, item.currency) }}</template>
          <template #marketValue="{ item }">{{ formatCurrency(item.units * item.price, item.currency) }}</template>
          <template #open_pnl="{ item }">
             <span :class="item.open_pnl >= 0 ? 'text-success' : 'text-danger'">
              {{ formatCurrency(item.open_pnl, item.currency) }}
            </span>
          </template>
        </BaseTable>
      </section>

      <!-- Orders Section -->
      <section>
        <h2>Recent Orders (Last 30 Days)</h2>
        <BaseTable v-if="recentOrders.length > 0" :headers="orderHeaders" :items="recentOrders">
           <template #limit_price="{ item }">{{ formatCurrency(item.limit_price, holdings.balances[0]?.currency_code) }}</template>
           <template #time_placed="{ item }">{{ formatDate(item.time_placed) }}</template>
        </BaseTable>
        <p v-else class="no-data-msg">No recent orders found.</p>
      </section>

      <!-- Balances Section -->
      <section>
        <h2>Cash Balances</h2>
        <div class="balances-grid">
          <div v-for="balance in holdings.balances" :key="balance.currency_code" class="summary-card">
            <span class="label">{{ balance.currency_code }} Cash</span>
            <span class="value">{{ formatCurrency(balance.cash_amount, balance.currency_code) }}</span>
          </div>
          <div v-for="balance in holdings.balances" :key="balance.currency_code + '_bp'" class="summary-card">
            <span class="label">{{ balance.currency_code }} Buying Power</span>
            <span class="value">{{ formatCurrency(balance.buying_power, balance.currency_code) }}</span>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
.account-holdings-view {
  width: 100%;
  padding: var(--semantic-size-inset-xl);
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--semantic-size-stack-md);
  padding: var(--semantic-size-inset-xl);
  color: var(--semantic-color-text-secondary);
}

.error-state h2 {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-danger);
}

.holdings-content {
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

section h2 {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-md);
}

.summary-section, .balances-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--semantic-size-stack-md);
}

.summary-card {
  background: var(--semantic-color-bg-subtle);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
}

.summary-card .label {
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
}

.summary-card .value {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
}

.text-success {
  color: var(--semantic-color-text-success);
}

.text-danger {
  color: var(--semantic-color-text-danger);
}

.no-data-msg {
  color: var(--semantic-color-text-secondary);
}
</style>
