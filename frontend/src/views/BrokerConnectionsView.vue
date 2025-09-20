<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useUiStore } from '@/stores/uiStore';
import apiClient from '@/services/api';
import BaseButton from '@/components/ui/BaseButton.vue';
import IconButton from '@/components/ui/IconButton.vue';
import PlusIcon from '@/components/icons/PlusIcon.vue';
import SettingsIcon from '@/components/icons/SettingsIcon.vue';
import TrashIcon from '@/components/icons/TrashIcon.vue';
import RefreshIcon from '@/components/icons/RefreshIcon.vue';
import BaseTable from '@/components/ui/BaseTable.vue';
import BaseModal from '@/components/ui/BaseModal.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';

const authStore = useAuthStore();
const uiStore = useUiStore();
const router = useRouter();

const user = computed(() => authStore.user);
const isRegistering = ref(false);
const isGeneratingLink = ref(false);
const isLoadingConnections = ref(true);
const connections = ref([]);

// State for Reconnect Modal
const showReconnectConfirmation = ref(false);
const connectionToReconnect = ref(null);

// State for Refresh Modal
const showRefreshConfirmation = ref(false);
const connectionToRefresh = ref(null);

// State for Delete Modal
const showDeleteConfirmation = ref(false);
const connectionToDelete = ref(null);

const tableHeaders = [
  { key: 'brokerage_name', text: 'Broker' },
  { key: 'created_at', text: 'Connected On' },
  { key: 'status', text: 'Status' },
  { key: 'actions', text: 'Actions' },
];

const isSnapTradeUserRegistered = computed(() => {
  return user.value?.profile?.has_snaptrade_user_secret === true;
});

const handleRegister = async () => {
  isRegistering.value = true;
  try {
    await authStore.registerWithSnapTrade();
    uiStore.showNotification({
      message: 'SnapTrade profile created successfully!',
      type: 'success',
    });
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'An unknown error occurred.';
    uiStore.showNotification({
      message: `Error: ${errorMessage}`,
      type: 'error',
    });
  } finally {
    isRegistering.value = false;
  }
};

const handleGenerateLink = async () => {
  isGeneratingLink.value = true;
  try {
    const redirectURI = await authStore.generateConnectionLink();
    if (redirectURI) {
      window.location.href = redirectURI;
    }
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'Could not generate connection link.';
    uiStore.showNotification({
      message: `Error: ${errorMessage}`,
      type: 'error',
    });
  } finally {
    isGeneratingLink.value = false;
  }
};

async function fetchConnections() {
  isLoadingConnections.value = true;
  try {
    const response = await apiClient.get('/api/v1/snaptrade/connections');
    connections.value = response.data;
  } catch (error) {
    uiStore.showNotification({ message: 'Failed to fetch connections.', type: 'error' });
  } finally {
    isLoadingConnections.value = false;
  }
}

function getRefreshInfo(connection) {
  const count = connection.manual_refresh_count || 0;
  const lastRefresh = connection.last_manual_refresh_at;
  const maxRefreshes = 3;

  let usedToday = 0;
  if (lastRefresh) {
    const lastRefreshDateUTC = new Date(lastRefresh).toISOString().split('T')[0];
    const todayUTC = new Date().toISOString().split('T')[0];
    if (lastRefreshDateUTC === todayUTC) {
      usedToday = count;
    }
  }

  const available = Math.max(0, maxRefreshes - usedToday);
  const isDisabled = available <= 0;

  const plural = available === 1 ? 'attempt' : 'attempts';
  const counterTooltip = `You have ${available} refresh ${plural} left today.`;

  const buttonTooltip = isDisabled
    ? 'Daily limit reached. Try again tomorrow.'
    : 'Force refresh holdings';

  return {
    isDisabled,
    showCounter: !isDisabled,
    counterText: `(${available}/${maxRefreshes})`,
    counterTooltip,
    buttonTooltip,
  };
}

function openRefreshConfirmation(connection) {
  connectionToRefresh.value = connection;
  showRefreshConfirmation.value = true;
}

async function handleConfirmRefresh() {
  if (!connectionToRefresh.value) return;

  const connectionId = connectionToRefresh.value.id;
  const connectionName = connectionToRefresh.value.brokerage_display_name || connectionToRefresh.value.brokerage_name;

  try {
    await apiClient.post(`/api/v1/snaptrade/connections/${connectionId}/refresh`);

    uiStore.showNotification({
      message: `✅ Update for ${connectionName} successfully started!`,
      type: 'success',
    });

    // Manually update the connection state locally for instant UI feedback
    const refreshedConnection = connections.value.find(c => c.id === connectionId);
    if (refreshedConnection) {
      refreshedConnection.manual_refresh_count = (refreshedConnection.manual_refresh_count || 0) + 1;
      refreshedConnection.last_manual_refresh_at = new Date().toISOString();
    }

  } catch (error) {
    if (error.response?.status === 429) {
      uiStore.showNotification({
        message: '⚠️ You have reached the daily update limit for this connection.',
        type: 'warning',
      });
      // Also disable the button immediately by updating the local state
      const refreshedConnection = connections.value.find(c => c.id === connectionId);
      if (refreshedConnection) {
        refreshedConnection.manual_refresh_count = 3;
        refreshedConnection.last_manual_refresh_at = new Date().toISOString();
      }
    } else {
      const errorMessage = error.response?.data?.detail || 'Failed to start the update.';
      uiStore.showNotification({
        message: `Error: ${errorMessage}`,
        type: 'error',
      });
    }
  } finally {
    showRefreshConfirmation.value = false;
    connectionToRefresh.value = null;
  }
}

function openReconnectConfirmation(connection) {
  connectionToReconnect.value = connection;
  showReconnectConfirmation.value = true;
}

async function handleReconnect() {
  if (!connectionToReconnect.value) return;

  try {
    const response = await apiClient.post('/api/v1/snaptrade/reconnect-link', {
      connection_id: connectionToReconnect.value.id,
    });
    const redirectURI = response.data.redirectURI;
    if (redirectURI) {
      window.location.href = redirectURI;
    }
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'Could not generate reconnect link.';
    uiStore.showNotification({
      message: `Error: ${errorMessage}`,
      type: 'error',
    });
  } finally {
    showReconnectConfirmation.value = false;
    connectionToReconnect.value = null;
  }
}

function openDeleteConfirmation(connection) {
  connectionToDelete.value = connection;
  showDeleteConfirmation.value = true;
}

async function handleConfirmDelete() {
  if (!connectionToDelete.value) return;

  try {
    await apiClient.delete(`/api/v1/snaptrade/connections/${connectionToDelete.value.id}`);
    uiStore.showNotification({
      message: '✅ Connection deleted successfully',
      type: 'success',
    });
    // Remove the connection from the local list
    connections.value = connections.value.filter(c => c.id !== connectionToDelete.value.id);
  } catch (error) {
    const errorMessage = error.response?.data?.message || 'Could not delete connection.';
    uiStore.showNotification({
      message: `Error: ${errorMessage}`,
      type: 'error',
    });
  } finally {
    showDeleteConfirmation.value = false;
    connectionToDelete.value = null;
  }
}

function navigateToAccounts(connection) {
  router.push({
    name: 'connection-accounts',
    params: { connectionId: connection.id },
  });
}

function formatDate(isoString) {
  if (!isoString) return '';
  const date = new Date(isoString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${day}/${month}/${year} ${hours}:${minutes}`;
}

onMounted(async () => {
  await authStore.fetchUser();
  if (isSnapTradeUserRegistered.value) {
    fetchConnections();
  }
});
</script>

<template>
  <div class="connections-view">
    <header class="view-header">
      <h1>Broker Connections</h1>
      <p>Manage your broker connections to sync your trading data.</p>
    </header>

    <div v-if="!isSnapTradeUserRegistered" class="registration-step">
      <h2>Step 1: Create Your Sync Profile</h2>
      <p>
        To connect your broker accounts, you must first create a secure profile on SnapTrade.
        This step is only required once.
      </p>
      <div class="action-bar">
        <BaseButton variant="primary" @click="handleRegister" :disabled="isRegistering">
          <SettingsIcon v-if="isRegistering" class="spin" />
          <PlusIcon v-else />
          <span class="button-text">Create SnapTrade Profile</span>
        </BaseButton>
      </div>
    </div>

    <div v-else class="connections-management">
       <div class="action-bar">
        <BaseButton variant="primary" @click="handleGenerateLink" :disabled="isGeneratingLink">
          <SettingsIcon v-if="isGeneratingLink" class="spin" />
          <PlusIcon v-else />
          <span class="button-text">Add New Connection</span>
        </BaseButton>
      </div>
      <div class="connections-list">
        <h2>Your Connections</h2>
        <div v-if="isLoadingConnections" class="flex justify-center p-8">
          <LoadingSpinner />
        </div>
        <div v-else-if="connections.length > 0">
          <BaseTable :headers="tableHeaders" :items="connections" :row-clickable="true" @row-click="navigateToAccounts">
            <template #brokerage_name="{ item }">
              <div class="broker-cell">
                <img v-if="item.brokerage_logo_url" :src="item.brokerage_logo_url" alt="" class="broker-logo">
                <span class="broker-name">{{ item.brokerage_display_name || item.brokerage_name }}</span>
              </div>
            </template>
            <template #created_at="{ item }">
              <span>{{ formatDate(item.created_at) }}</span>
            </template>
            <template #status="{ item }">
              <span :class="item.disabled ? 'status-disabled' : 'status-active'">
                {{ item.disabled ? 'Disabled' : 'Active' }}
              </span>
            </template>
            <template #actions="{ item }">
              <div class="actions-cell">
                <BaseButton v-if="item.disabled" @click.stop="openReconnectConfirmation(item)" variant="secondary" size="small">
                  Reconnect
                </BaseButton>

                <template v-if="!item.disabled">
                  <IconButton
                    @click.stop="openRefreshConfirmation(item)"
                    :disabled="getRefreshInfo(item).isDisabled"
                    :title="getRefreshInfo(item).buttonTooltip"
                    aria-label="Refresh connection holdings"
                    class="refresh-btn-hover"
                  >
                    <RefreshIcon />
                  </IconButton>
                </template>

                <IconButton
                  @click.stop="openDeleteConfirmation(item)"
                  aria-label="Delete connection"
                  color="var(--semantic-color-feedback-negative-text)"
                  class="delete-btn-hover"
                >
                  <TrashIcon />
                </IconButton>
              </div>
            </template>
          </BaseTable>
        </div>
        <div v-else class="no-connections">
          <p>Sync profile created! You can now add your first connection.</p>
          <p>Click "Add New Connection" to get started.</p>
        </div>
      </div>
    </div>

    <ConfirmationModal
      :show="showRefreshConfirmation"
      title="Force Holdings Update"
      confirmation-word="update"
      @close="showRefreshConfirmation = false"
      @confirm="handleConfirmRefresh"
    >
      <p>This will start a background synchronization for this connection's holdings.</p>
      <p class="mt-2">You can perform this action up to 3 times per day for each connection.</p>
    </ConfirmationModal>

    <ConfirmationModal
      :show="showReconnectConfirmation"
      title="Reconnect Brokerage"
      confirmation-word="reconnect"
      @close="showReconnectConfirmation = false"
      @confirm="handleReconnect"
    >
      <p>You will be redirected to SnapTrade to re-authenticate with this brokerage.</p>
    </ConfirmationModal>

    <ConfirmationModal
      :show="showDeleteConfirmation"
      title="Delete Connection"
      confirmation-word="delete"
      @close="showDeleteConfirmation = false"
      @confirm="handleConfirmDelete"
    >
      <p class="text-gray-700 dark:text-gray-300">
        Are you sure you want to delete this connection? All associated accounts and holdings will be removed.
        <br />
        <strong class="font-bold text-red-600 dark:text-red-400">This action cannot be undone.</strong>
      </p>
    </ConfirmationModal>

  </div>
</template>

<style scoped>
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
.spin {
  animation: spin 1s linear infinite;
}

.connections-view {
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

.action-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--semantic-size-stack-md);
}

.connections-list h2 {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-md);
}

.no-connections {
  background-color: var(--semantic-color-bg-subtle);
  border: 1px solid var(--semantic-color-border-subtle);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--semantic-size-inset-lg);
  text-align: center;
  color: var(--semantic-color-text-secondary);
}

.registration-step h2 {
    font: var(--semantic-font-style-heading-lg);
    color: var(--semantic-color-text-primary);
    margin-bottom: var(--semantic-size-stack-sm);
}

.registration-step p {
    color: var(--semantic-color-text-secondary);
    margin-bottom: var(--semantic-size-stack-md);
}

/* Broker column styles */
.broker-cell {
  display: flex;
  align-items: center;
  gap: 1rem; /* 16px */
}
.broker-logo {
  height: 109px;
  width: 109px;
  border-radius: 50%;
  object-fit: contain;
}
.broker-name {
  font-weight: var(--semantic-font-weight-medium);
  color: var(--semantic-color-text-primary);
}

@media (max-width: 768px) {
  .broker-cell, .actions-cell {
    justify-content: flex-end;
  }
  .broker-logo {
    height: 48px;
    width: 48px;
  }
  .broker-name {
    font: var(--semantic-font-style-body-xs);
  }
}

/* Status column styles */
.status-active {
  color: var(--semantic-color-text-success);
}
.status-disabled {
  color: var(--semantic-color-text-danger);
}

/* Actions column styles */
.actions-cell {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.5rem; /* 8px */
}
.refresh-btn-hover,
.delete-btn-hover {
  opacity: 0.8;
  transition: opacity 0.2s ease-in-out;
}
.refresh-btn-hover:hover,
.delete-btn-hover:hover {
  opacity: 1;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--semantic-size-stack-md);
  padding: var(--semantic-size-inset-sm);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xxs);
}

.detail-item .label {
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
}

.detail-item .value {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-primary);
}

.capitalize {
  text-transform: capitalize;
}
</style>
