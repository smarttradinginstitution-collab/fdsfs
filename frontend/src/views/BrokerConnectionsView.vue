<script setup>
import { computed, ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useUiStore } from '@/stores/uiStore';
import BaseButton from '@/components/ui/BaseButton.vue';
import PlusIcon from '@/components/icons/PlusIcon.vue';
import SettingsIcon from '@/components/icons/SettingsIcon.vue';

const authStore = useAuthStore();
const uiStore = useUiStore();

const user = computed(() => authStore.user);
const isRegistering = ref(false);
const isGeneratingLink = ref(false);

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

onMounted(() => {
  authStore.fetchUser();
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
        <div v-if="user && user.brokerage_connections && user.brokerage_connections.length > 0">
          <ul>
            <li v-for="conn in user.brokerage_connections" :key="conn.id">
              {{ conn.brokerage_name }} - {{ conn.status }}
            </li>
          </ul>
        </div>
        <div v-else class="no-connections">
          <p>Profilo di sincronizzazione creato! Ora puoi aggiungere la tua prima connessione.</p>
          <p>Clicca su "Aggiungi Nuova Connessione" per iniziare.</p>
        </div>
      </div>
    </div>

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
