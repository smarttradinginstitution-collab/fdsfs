<!--
// =============================================================================
// FILE: components/layout/AppSidebar.vue
// DESCRIZIONE: Sidebar principale dell'applicazione, ora collassabile.
// Gestisce il suo stato (aperta/chiusa) tramite il `uiStore`.
// =============================================================================
-->

<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import { useUiStore } from '../../stores/uiStore';
import { useAuthStore } from '../../stores/auth';
import apiClient from '@/services/api';
import ThemeToggle from '../ui/ThemeToggle.vue';
import BaseButton from '../ui/BaseButton.vue';

const uiStore = useUiStore();
const authStore = useAuthStore();

const navLinks = [
  { to: '/', text: 'Dashboard', icon: 'D' },
  { to: '/trades', text: 'Trades', icon: 'T' },
  { to: '/analytics', text: 'Analytics', icon: 'A' },
  { to: '#', text: 'Settings', icon: 'S' },
];

// Logic moved from DashboardHeader
const users = ref([]);
const loadingUsers = ref(false);
const errorUsers = ref(null);

async function fetchUsers() {
  if (!authStore.isAuthenticated) return;
  loadingUsers.value = true;
  errorUsers.value = null;
  try {
    const res = await apiClient.get('/api/v1/users/');
    users.value = res.data;
  } catch (err) {
    console.error('Errore caricamento utenti:', err);
    errorUsers.value = 'Impossibile caricare gli utenti';
  } finally {
    loadingUsers.value = false;
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchUsers();
  }
});
</script>

<template>
  <aside class="sidebar" :class="{ 'is-collapsed': uiStore.isSidebarCollapsed, 'is-mobile-open': uiStore.isMobileMenuOpen }">
    <div class="sidebar-header">
      <span v-if="!uiStore.isSidebarCollapsed">TRZ</span>
      <span v-else>T</span>
      <button @click="uiStore.toggleSidebar" class="toggle-button">
        &lt;
      </button>
    </div>

    <nav class="sidebar-nav">
      <RouterLink
        v-for="link in navLinks"
        :key="link.text"
        :to="link.to"
        class="nav-item"
        @click="uiStore.closeMobileMenu"
      >
        <span class="nav-icon">{{ link.icon }}</span>
        <span v-if="!uiStore.isSidebarCollapsed" class="nav-text">{{ link.text }}</span>
      </RouterLink>
    </nav>

    <!-- New footer with dynamic data, pushed to the bottom -->
    <div class="sidebar-footer">
      <div v-if="!uiStore.isSidebarCollapsed">
        <ThemeToggle />

        <div v-if="authStore.isAuthenticated" class="users-info footer-block">
          <span v-if="loadingUsers">Caricamento...</span>
          <span v-else-if="errorUsers">{{ errorUsers }}</span>
          <span v-else>Utenti totali: {{ users.length }}</span>
        </div>

        <div v-if="authStore.isAuthenticated && authStore.user" class="user-profile footer-block">
          <div class="avatar">
            {{ authStore.user.email.substring(0, 2).toUpperCase() }}
          </div>
          <div class="user-details">
            <p class="user-email">{{ authStore.user.email }}</p>
            <p class="user-role" v-if="authStore.user.roleName">({{ authStore.user.roleName }})</p>
          </div>
        </div>

        <BaseButton v-if="authStore.isAuthenticated" variant="secondary" size="small" @click="authStore.logout" class="logout-button">
          Logout
        </BaseButton>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  z-index: var(--base-layer-z-index-sticky);
  width: var(--semantic-size-component-sidebar-width-expanded); /* Usa il nuovo token */
  height: 100vh;
  background-color: var(--base-color-gray-900);
  border-right: var(--base-border-width-1) solid var(--semantic-color-border-default);
  display: flex;
  flex-direction: column;
  padding: var(--semantic-size-inset-lg);
  /* Transizione fluida per la larghezza. */
  transition: width var(--base-animation-duration-base) var(--base-animation-easing-out);
}

/* Stili per lo stato collassato */
.sidebar.is-collapsed {
  width: var(--base-size-component-sidebar-width-collapsed); /* Usa il nuovo token */
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font: var(--semantic-font-style-heading-2xl);
  font-weight: var(--base-font-weight-extrabold);
  margin-bottom: var(--semantic-size-stack-xl);
}

.toggle-button {
  background: none;
  border: none;
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  transition: all var(--base-animation-duration-fast);
}
.toggle-button:hover {
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-primary);
}
/* Ruotiamo il pulsante quando la sidebar è collassata. */
.sidebar.is-collapsed .toggle-button {
  transform: rotate(180deg);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  flex-grow: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
  text-decoration: none;
  padding: var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-interactive);
  transition: all var(--base-animation-duration-fast);
  white-space: nowrap; /* Impedisce al testo di andare a capo durante la transizione */
  overflow: hidden; /* Nasconde il testo che fuoriesce */
}
/* Centra l'icona quando la sidebar è collassata */
.sidebar.is-collapsed .nav-item {
  justify-content: center;
}
.nav-icon {
  font-weight: bold;
  min-width: 20px;
  text-align: center;
}

.nav-item:hover,
.nav-item.router-link-active {
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-primary);
}

.sidebar-footer {
  margin-top: auto; /* Pushes the footer to the bottom */
  padding-top: var(--semantic-size-stack-lg);
  border-top: 1px solid var(--semantic-color-border-default);
}

.sidebar-footer > div {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.footer-block {
  padding: var(--semantic-size-inset-sm);
  background-color: var(--semantic-color-surface-secondary);
  border-radius: var(--semantic-border-radius-interactive);
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  overflow: hidden;
}

.avatar {
  min-width: var(--base-size-component-avatar-md);
  height: var(--base-size-component-avatar-md);
  border-radius: var(--base-border-radius-full);
  background-color: var(--semantic-color-interactive-primary-default);
  color: var(--semantic-color-text-on-brand);
  display: grid;
  place-items: center;
  font: var(--semantic-font-style-label-md);
  flex-shrink: 0;
}

.user-details {
  overflow: hidden;
  white-space: nowrap;
}

.user-email {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-primary);
}

.user-role {
  font: var(--semantic-font-style-body-xs);
  color: var(--semantic-color-text-secondary);
}

.logout-button {
  width: 100%;
}

.nav-text {
  /* Effetto di dissolvenza per il testo */
  transition: opacity var(--base-animation-duration-fast);
}
.sidebar.is-collapsed .sidebar-footer > div,
.sidebar.is-collapsed .nav-text {
  opacity: 0;
}


/* --- Media Query per il comportamento Mobile --- */
@media (max-width: 768px) {
  .sidebar {
    /* Su mobile, la sidebar è un overlay che appare da sinistra */
    position: fixed;
    z-index: var(--base-layer-z-index-sidebar-overlay);
    transform: translateX(-100%); /* Nascosta di default */
    transition: transform var(--base-animation-duration-base) var(--base-animation-easing-out);

    /* Su mobile, non vogliamo mai la versione "collassata", ma sempre quella estesa */
    width: var(--semantic-size-component-sidebar-width-expanded) !important;
  }

  /* Quando il menu mobile è aperto, la facciamo apparire */
  .sidebar.is-mobile-open {
    transform: translateX(0);
  }

  /* Nascondiamo il bottone per collassare la sidebar, dato che non serve su mobile */
  .toggle-button {
    display: none;
  }

  /* Forziamo la visualizzazione del testo dei link, ignorando lo stato `is-collapsed` */
  .sidebar.is-collapsed .nav-text,
  .sidebar.is-collapsed .user-info {
    opacity: 1;
  }
}
</style>
