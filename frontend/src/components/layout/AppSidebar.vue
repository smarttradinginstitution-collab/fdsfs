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
import { computed } from 'vue';

// --- STORE ---
const uiStore = useUiStore();
const authStore = useAuthStore();

// --- DATI DEL COMPONENTE ---
const user = computed(() => {
  if (!authStore.user) {
    return { name: 'Guest', initials: 'G', email: '' };
  }
  const email = authStore.user.email || '';
  const name = authStore.user.user_metadata?.full_name || email.split('@')[0];
  const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  return { name, initials, email };
});

// Dati per i link di navigazione.
const navLinks = [
  { to: '/', text: 'Dashboard', icon: 'D', type: 'link' },
  { to: '/trades', text: 'Trades', icon: 'T', type: 'link' },
  { to: '/analytics', text: 'Analytics', icon: 'A', type: 'link' },
  { to: '#', text: 'Settings', icon: 'S', type: 'button', action: () => uiStore.openSettingsModal() },
];

function handleItemClick(item) {
  if (item.action) {
    item.action();
  }
  uiStore.closeMobileMenu();
}
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
      <template v-for="link in navLinks" :key="link.text">
        <RouterLink
          v-if="link.type === 'link'"
          :to="link.to"
          class="nav-item"
          @click="handleItemClick(link)"
        >
          <span class="nav-icon">{{ link.icon }}</span>
          <span v-if="!uiStore.isSidebarCollapsed" class="nav-text">{{ link.text }}</span>
        </RouterLink>
        <button
          v-else-if="link.type === 'button'"
          class="nav-item"
          @click="handleItemClick(link)"
        >
          <span class="nav-icon">{{ link.icon }}</span>
          <span v-if="!uiStore.isSidebarCollapsed" class="nav-text">{{ link.text }}</span>
        </button>
      </template>
    </nav>

    <div class="sidebar-footer">
      <div class="avatar">
        {{ user.initials }}
      </div>
      <div v-if="!uiStore.isSidebarCollapsed" class="user-info">
        <p class="user-name">{{ user.name }}</p>
        <p class="user-email">{{ user.email }}</p>
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
  /* Effetto di dissolvenza per il testo */
  transition: opacity var(--base-animation-duration-fast);
}
.sidebar.is-collapsed .user-info,
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
