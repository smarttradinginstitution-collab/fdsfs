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
import logo from '../../assets/images/logo.svg';

// Importiamo le icone necessarie
import ViewGridIcon from '../icons/ViewGridIcon.vue';
import BuildingLibraryIcon from '../icons/BuildingLibraryIcon.vue';
import ViewListIcon from '../icons/ViewListIcon.vue';
import SparkleIcon from '../icons/SparkleIcon.vue';
import SettingsIcon from '../icons/SettingsIcon.vue';
import BookOpenIcon from '../icons/BookOpenIcon.vue';
import TagIcon from '../icons/TagIcon.vue';
import ChartBarIcon from '../icons/ChartBarIcon.vue';

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
  { to: '/', text: 'Dashboard', icon: ViewGridIcon },
  { to: '/playbooks', text: 'Playbooks', icon: BuildingLibraryIcon },
  { to: '/trades', text: 'Trades', icon: ViewListIcon },
  { to: '/notebook', text: 'Notebook', icon: BookOpenIcon },
  { to: '/analytics', text: 'Analytics', icon: SparkleIcon },
  { to: '/settings/tags', text: 'Tags', icon: TagIcon },
  { to: '#', text: 'Settings', icon: SettingsIcon },
];
</script>

<template>
  <!--
  Oltre a `is-collapsed` per desktop, aggiungiamo `is-mobile-open` per gestire
  la visibilità su schermi piccoli come un overlay.
  -->
  <aside class="sidebar" :class="{ 'is-collapsed': uiStore.isSidebarCollapsed, 'is-mobile-open': uiStore.isMobileMenuOpen }">
    <div class="sidebar-header">
        <div v-if="!uiStore.isSidebarCollapsed" class="logo-container">
        <span>Trade</span><img :src="logo" alt="TradeVantage" class="logo" /><span>antage</span>

      </div>
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
        <component :is="link.icon" class="nav-icon" />
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

<style lang="scss" scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: var(
    --semantic-size-component-sidebar-width-expanded
  ); /* Usa il nuovo token */
  height: 100vh;
  background-color: var(--base-color-gray-900);
  border-right: var(--base-border-width-1) solid
    var(--semantic-color-border-default);
  display: flex;
  flex-direction: column;
  padding: var(--semantic-size-inset-lg);
  /* Transizione fluida per la larghezza. */
  transition: width var(--base-animation-duration-base)
    var(--base-animation-easing-out);
}

/* Stili per lo stato collassato */
.sidebar.is-collapsed {
  width: var(
    --base-size-component-sidebar-width-collapsed
  ); /* Usa il nuovo token */
}

.sidebar-header {
  display: flex;
  align-items: start;
  justify-content: space-between;
  font: var(--semantic-font-style-heading-xs);
  font-weight: var(--base-font-weight-extrabold);
  margin-bottom: var(--semantic-size-stack-xl);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-xs);
}

.logo {
  height: 40px;
  margin-left: -15px;
  margin-right: -10px;
  width: auto;
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
.logout-button:hover,
.mfa-button:hover,
.mfa-button-active:hover {
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-primary);
}

.mfa-button,
.mfa-button-active {
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
  width: 20px;
  height: 20px;
  flex-shrink: 0; /* Impedisce all'icona di restringersi */
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

.user-info,
.nav-text {
  /* Effetto di dissolvenza per il testo */
  transition: opacity var(--base-animation-duration-fast);
}
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

.logout-button:hover,
.mfa-button:hover,
.mfa-button-active:hover {
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-primary);
}

.mfa-button,
.mfa-button-active {
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

/* --- Media Query per il comportamento Mobile --- */
@include media-down('md') {
  .sidebar {
    /* Su mobile, la sidebar è un overlay che appare da sinistra */
    position: fixed;
    transform: translateX(-100%); /* Nascosta di default */
    transition: transform var(--base-animation-duration-base)
      var(--base-animation-easing-out);

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