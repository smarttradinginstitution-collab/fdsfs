<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { supabase } from '@/services/supabase';
import apiClient from '@/services/api';

const router = useRouter();
const message = ref('Verifica in corso, attendere prego...');
const error = ref('');

onMounted(() => {
  const { data: authListener } = supabase.auth.onAuthStateChange(
    async (event, session) => {
      // Questo evento scatta al caricamento della pagina se l'utente
      // arriva dal link di conferma email.
      if (event === 'SIGNED_IN') {
        authListener.subscription.unsubscribe(); // Interrompiamo l'ascolto

        if (session && session.user) {
          try {
            message.value = 'Account email confermato. Creazione del profilo in corso...';

            // Chiamiamo il nostro backend per creare il GeneralAccount
            await apiClient.post('/general-accounts/', {
              // Il nostro backend si aspetta che il token sia nell'header,
              // l'interceptor di apiClient lo gestisce.
              // Mandiamo un body vuoto se non sono richiesti dati specifici.
            }, {
              headers: {
                Authorization: `Bearer ${session.access_token}`
              }
            });

            message.value = 'Profilo creato con successo! Verrai reindirizzato al login a breve.';

            // Reindirizza al login dopo un breve ritardo
            setTimeout(() => {
              router.push('/login');
            }, 3000);

          } catch (err) {
            console.error('Errore nella creazione del GeneralAccount:', err);
            error.value = err.response?.data?.detail || 'Impossibile creare il profilo utente. Si prega di contattare il supporto.';
          }
        }
      } else if (event === 'INITIAL_SESSION') {
        // Se c'è già una sessione ma non è quella che ci aspettiamo,
        // potrebbe essere un utente già loggato. Lo mandiamo al login.
        authListener.subscription.unsubscribe();
        router.push('/login');
      }
    }
  );
});
</script>

<template>
  <div class="callback-view">
    <div class="callback-container">
      <div v-if="error" class="error-message">
        <h1>Errore</h1>
        <p>{{ error }}</p>
        <RouterLink to="/login">Torna al Login</RouterLink>
      </div>
      <div v-else class="loading-message">
        <h1>{{ message }}</h1>
        <p>Non chiudere questa pagina.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.callback-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  text-align: center;
  background-color: var(--semantic-color-surface-page);
}

.callback-container {
  padding: var(--semantic-size-stack-xl);
}

h1 {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-md);
}

p {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-secondary);
}

.error-message {
  color: var(--semantic-color-text-negative);
}

.error-message a {
  display: inline-block;
  margin-top: var(--semantic-size-stack-lg);
  color: var(--semantic-color-text-action-primary-default);
}
</style>