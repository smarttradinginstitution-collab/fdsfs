<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '@/services/api';
import { useUiStore } from '@/stores/uiStore';
import BaseTable from '@/components/ui/BaseTable.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';

const route = useRoute();
const uiStore = useUiStore();

const accounts = ref([]);
const isLoading = ref(true);
const connectionId = computed(() => route.params.connectionId);

const tableHeaders = [
  { key: 'name', text: 'Account Name' },
  { key: 'institution_name', text: 'Broker' },
  { key: 'number', text: 'Account Number' },
  { key: 'balance', text: 'Balance' },
];

function formatCurrency(value, currency) {
  if (typeof value !== 'number') {
    return '';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
  }).format(value);
}

onMounted(async () => {
  if (!connectionId.value) {
    uiStore.showNotification({ message: 'No connection ID provided.', type: 'error' });
    isLoading.value = false;
    return;
  }

  try {
    const response = await apiClient.get(`/api/v1/snaptrade/accounts`, {
      params: { connection_id: connectionId.value }
    });

    accounts.value = response.data.accounts;

    if (response.data.warning) {
      uiStore.showNotification({
        message: response.data.warning.message,
        type: 'warning',
        duration: 5000
      });
    }

  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'Failed to fetch accounts.';
    uiStore.showNotification({ message: errorMessage, type: 'error' });
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div class="account-list-view">
    <header class="view-header">
      <h1>Trading Accounts</h1>
      <p>A list of all your trading accounts for the selected connection.</p>
    </header>

    <div class="account-list">
      <div v-if="isLoading" class="flex justify-center p-8">
        <LoadingSpinner />
      </div>
      <div v-else-if="accounts.length > 0">
        <BaseTable :headers="tableHeaders" :items="accounts" :row-clickable="true">
          <template #name="{ item }">
            <span class="font-medium">{{ item.name }}</span>
          </template>
          <template #balance="{ item }">
            <span>{{ formatCurrency(item.balance, item.currency) }}</span>
          </template>
        </BaseTable>
      </div>
      <div v-else class="no-accounts">
        <p>No trading accounts found for this connection.</p>
        <p>This may be because the initial sync is still in progress. Please check back in a few moments.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.account-list-view {
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

.account-list {
  /* Style for the list container */
}

.no-accounts {
  background-color: var(--semantic-color-bg-subtle);
  border: 1px solid var(--semantic-color-border-subtle);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--semantic-size-inset-lg);
  text-align: center;
  color: var(--semantic-color-text-secondary);
}

/* Add hover effect for clickable rows in BaseTable */
:deep(.base-table tbody tr:hover) {
  background-color: var(--semantic-color-bg-subtle-hover);
  cursor: pointer;
}
</style>
