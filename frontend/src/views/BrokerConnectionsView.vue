<script setup>
import { computed, ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useUiStore } from '@/stores/uiStore';
import apiClient from '@/services/api';
import BaseButton from '@/components/ui/BaseButton.vue';
import PlusIcon from '@/components/icons/PlusIcon.vue';
import SettingsIcon from '@/components/icons/SettingsIcon.vue';
import BaseTable from '@/components/ui/BaseTable.vue';
import ConfirmationModal from '@/components/ui/ConfirmationModal.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';

const authStore = useAuthStore();
const uiStore = useUiStore();

const user = computed(() => authStore.user);
const isRegistering = ref(false);
const isGeneratingLink = ref(false);
const isLoadingConnections = ref(true);
const connections = ref([]);
const showReconnectConfirmation = ref(false);
const connectionToReconnect = ref(null);

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
      message: 'Profilo SnapTrade creato con successo!',
      type: 'success',
    });
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'Si è verificato un errore sconosciuto.';
    uiStore.showNotification({
      message: `Errore: ${errorMessage}`,
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
    const errorMessage = error.response?.data?.detail || 'Impossibile generare il link di connessione.';
    uiStore.showNotification({
      message: `Errore: ${errorMessage}`,
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
    const errorMessage = error.response?.data?.detail || 'Impossibile generare il link di riconnessione.';
    uiStore.showNotification({
      message: `Errore: ${errorMessage}`,
      type: 'error',
    });
  } finally {
    showReconnectConfirmation.value = false;
    connectionToReconnect.value = null;
  }
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
      <h1>Connessioni Broker</h1>
      <p>Gestisci le tue connessioni ai broker per sincronizzare i tuoi dati di trading.</p>
    </header>

    <div v-if="!isSnapTradeUserRegistered" class="registration-step">
      <h2>Passo 1: Crea il tuo profilo di Sincronizzazione</h2>
      <p>
        Per poter collegare i tuoi conti broker, devi prima creare un profilo sicuro su SnapTrade.
        Questo passaggio è richiesto solo una volta.
      </p>
      <div class="action-bar">
        <BaseButton variant="primary" @click="handleRegister" :disabled="isRegistering">
          <SettingsIcon v-if="isRegistering" class="spin" />
          <PlusIcon v-else />
          <span class="button-text">Crea Profilo SnapTrade</span>
        </BaseButton>
      </div>
    </div>

    <div v-else class="connections-management">
       <div class="action-bar">
        <BaseButton variant="primary" @click="handleGenerateLink" :disabled="isGeneratingLink">
          <SettingsIcon v-if="isGeneratingLink" class="spin" />
          <PlusIcon v-else />
          <span class="button-text">Aggiungi Nuova Connessione</span>
        </BaseButton>
      </div>
      <div class="connections-list">
        <h2>Le tue connessioni</h2>
        <div v-if="isLoadingConnections" class="flex justify-center p-8">
          <LoadingSpinner />
        </div>
        <div v-else-if="connections.length > 0">
          <BaseTable :headers="tableHeaders" :items="connections">
            <template #status="{ item }">
              <span :class="item.disabled ? 'text-red-500' : 'text-green-500'">
                {{ item.disabled ? 'Disabled' : 'Active' }}
              </span>
            </template>
            <template #actions="{ item }">
              <BaseButton v-if="item.disabled" @click="openReconnectConfirmation(item)" variant="secondary" size="small">
                Reconnect
              </BaseButton>
            </template>
          </BaseTable>
        </div>
        <div v-else class="no-connections">
          <p>Profilo di sincronizzazione creato! Ora puoi aggiungere la tua prima connessione.</p>
          <p>Clicca su "Aggiungi Nuova Connessione" per iniziare.</p>
        </div>
      </div>
    </div>

    <ConfirmationModal
      :show="showReconnectConfirmation"
      title="Reconnect Brokerage"
      confirmation-word="reconnect"
      @close="showReconnectConfirmation = false"
      @confirm="handleReconnect"
    >
      <p>Are you sure you want to reconnect this brokerage? You will be redirected to SnapTrade to re-authenticate.</p>
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
}

.connections-list h2 {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-md);
}

.no-connections {
  background-color: var(--semantic-color-bg-subtle);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--semantic-size-inset-lg);
  text-align: center;
}

.no-connections p {
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
</style>
