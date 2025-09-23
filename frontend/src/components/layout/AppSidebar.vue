<!--
// =============================================================================
// FILE: components/layout/AppSidebar.vue
// DESCRIZIONE: Sidebar principale dell'applicazione, ora collassabile.
// Gestisce il suo stato (aperta/chiusa) tramite il `uiStore`.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import { RouterLink } from 'vue-router';
import { useUiStore } from '../../stores/uiStore';
import { useAuthStore } from '../../stores/auth';
import ThemeToggle from '../ui/ThemeToggle.vue';
import MfaModal from '../mfa/MfaModal.vue'; // Importa la nuova modale
import { computed, ref } from 'vue';

// --- STORE ---
const uiStore = useUiStore();
const authStore = useAuthStore();

// --- DATI DEL COMPONENTE ---
const user = computed(() => authStore.user);
const isMfaActive = computed(() => authStore.isMfaActive);

// Stato per la modale MFA
const isMfaModalOpen = ref(false);
const mfaMode = ref('enroll'); // 'enroll' o 'disable'

function openMfaModal(mode) {
  mfaMode.value = mode;
  isMfaModalOpen.value = true;
}

// Dati per i link di navigazione.
// Usare un array rende più facile gestire l'aggiunta di icone in futuro.
const navLinks = [
  { to: '/', text: 'Dashboard', icon: 'D' },
  { to: '/trades', text: 'Trades', icon: 'T' },
  { to: '/analytics', text: 'Analytics', icon: 'A' },
  { to: '#', text: 'Settings', icon: 'S' },
];
</script>

<template>
  <!--
  Oltre a `is-collapsed` per desktop, aggiungiamo `is-mobile-open` per gestire
  la visibilità su schermi piccoli come un overlay.
  -->
  <aside class="sidebar" :class="{ 'is-collapsed': uiStore.isSidebarCollapsed, 'is-mobile-open': uiStore.isMobileMenuOpen }">
    <div class="sidebar-header">
      <span v-if="!uiStore.isSidebarCollapsed">TRZ</span>
      <span v-else>T</span>
      <!-- Questo pulsante ora è nascosto su mobile, dove usiamo l'hamburger. -->
      <button @click="uiStore.toggleSidebar" class="toggle-button">
        &lt;
      </button>
    </div>

    <nav class="sidebar-nav">
      <!--
      Aggiungiamo un evento @click per chiudere il menu mobile quando si
      seleziona un link, migliorando l'esperienza utente su mobile.
      -->
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

    <div class="sidebar-footer">
      <div class="user-profile" v-if="authStore.isAuthenticated && user">
        <div class="avatar">
          {{ user.email ? user.email.charAt(0).toUpperCase() : 'U' }}
        </div>
        <div v-if="!uiStore.isSidebarCollapsed" class="user-info">
          <p class="user-name">{{ user.email }}</p>
          <p class="user-role">{{ user.roleName }}</p>
        </div>
      </div>
      <div class="footer-actions" v-if="!uiStore.isSidebarCollapsed">
        <button v-if="!isMfaActive" @click="openMfaModal('enroll')" class="mfa-button">
          Attiva MFA
        </button>
        <button v-else @click="openMfaModal('disable')" class="mfa-button-active">
          Disattiva MFA
        </button>
        <button @click="authStore.logout" class="logout-button">
          Logout
        </button>
        <ThemeToggle />
      </div>
    </div>
  </aside>

  <MfaModal v-model="isMfaModalOpen" :mode="mfaMode" @success="(msg) => console.log(msg)" />
</template>

<style scoped>
/* Stili Mobile-First (default) */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  background-color: var(--base-color-gray-900);
  border-right: var(--base-border-width-1) solid var(--semantic-color-border-default);
  display: flex;
  flex-direction: column;
  padding: var(--semantic-size-inset-lg);
  z-index: var(--base-layer-z-index-nav); /* Assicura che la sidebar sia sopra il contenuto */

  /* Su mobile, la sidebar è un overlay che appare da sinistra */
  width: var(--semantic-size-component-sidebar-width-expanded);
  transform: translateX(-100%);
  transition: transform var(--base-animation-duration-base) var(--base-animation-easing-out);
}

/* Quando il menu mobile è aperto, la facciamo apparire */
.sidebar.is-mobile-open {
  transform: translateX(0);
}

/* Nascondiamo il bottone per collassare la sidebar su mobile */
.toggle-button {
  display: none;
}

/* Stili per lo stato collassato (solo desktop) */
.sidebar.is-collapsed {
  /* Su mobile questo non ha effetto perché la larghezza è fissa. */
  /* Su desktop, la transizione della larghezza si attiverà. */
  width: var(--semantic-size-component-sidebar-width-collapsed);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font: var(--semantic-font-style-heading-2xl);
  font-weight: var(--base-font-weight-extrabold);
  margin-bottom: var(--semantic-size-stack-xl);
}

.logout-button:hover, .mfa-button:hover, .mfa-button-active:hover {
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-primary);
}

.mfa-button, .mfa-button-active {
  background: none;
  border: 1px solid var(--semantic-color-border-default);
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--semantic-border-radius-interactive);
  transition: all var(--base-animation-duration-fast);
  flex-grow: 1; /* Make buttons share space */
  text-align: center;
}

.mfa-button-active {
  border-color: var(--semantic-color-border-success);
  color: var(--semantic-color-text-success);
}

/* Ruotiamo il pulsante quando la sidebar è collassata (solo desktop) */
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
  white-space: nowrap;
  overflow: hidden;
}

/* Centra l'icona quando la sidebar è collassata (solo desktop) */
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
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--semantic-size-stack-md);
  overflow: hidden;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.user-info, .nav-text {
  transition: opacity var(--base-animation-duration-fast);
}

/* Nascondi testo solo su desktop quando collassato */
.sidebar.is-collapsed .user-info,
.sidebar.is-collapsed .nav-text {
  opacity: 0;
}

.user-name {
  font-weight: bold;
}

.user-role {
  font-size: 0.8rem;
  color: var(--semantic-color-text-secondary);
}

.logout-button {
  background: none;
  border: 1px solid var(--semantic-color-border-default);
  color: var(--semantic-color-text-secondary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--semantic-border-radius-interactive);
  transition: all var(--base-animation-duration-fast);
}

/* Stili Desktop (da breakpoint 'md' in su) */
@include mq-md {
  .sidebar {
    /* Su desktop, la sidebar è sempre visibile e non si trasforma */
    transform: translateX(0);
    width: var(--semantic-size-component-sidebar-width-expanded);
    transition: width var(--base-animation-duration-base) var(--base-animation-easing-out);
  }

  .sidebar.is-collapsed {
    width: var(--semantic-size-component-sidebar-width-collapsed);
  }

  .toggle-button {
    display: grid; /* Ri-mostra il bottone per collassare */
  }

  /* Su desktop, l'opacità del testo deve rispettare lo stato collassato */
  .sidebar.is-collapsed .nav-text,
  .sidebar.is-collapsed .user-info {
    opacity: 0;
  }
}
</style>
