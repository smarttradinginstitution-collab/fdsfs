<!--
=============================================================================
FILE: components/layout/DashboardHeader.vue
DESCRIZIONE: Header con dati da /api/v1/users (per admin).
=============================================================================
-->
<script setup>
import { ref, onMounted } from 'vue';
import { useMediaQuery } from '@vueuse/core';
import HamburgerButton from '../ui/HamburgerButton.vue';
import DropdownButton from '../ui/DropdownButton.vue';
import StrategyFilter from '../dashboard/filters/StrategyFilter.vue';
import DateRangeFilter from '../dashboard/filters/DateRangeFilter.vue';
import { useUiStore } from '../../stores/uiStore';
import { useAuthStore } from '../../stores/auth';
import BaseButton from '../ui/BaseButton.vue';
import apiClient from '@/services/api'; // 👈 client axios configurato

// Import the icon components
import FilterIcon from '../icons/FilterIcon.vue';
import CalendarIcon from '../icons/CalendarIcon.vue';

const uiStore = useUiStore();
const authStore = useAuthStore();

defineProps({
  title: {
    type: String,
    required: true,
  },
});

// Stato per gli utenti
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

// carica utenti al mount (solo se loggato e admin)
onMounted(() => {
  fetchUsers();
});

// Logica responsive con VueUse
const isDesktop = useMediaQuery('(min-width: 769px)');
</script>

<template>
  <header class="header">
    <div class="header-left">
      <HamburgerButton class="hamburger-menu" :is-open="uiStore.isMobileMenuOpen" @toggle="uiStore.toggleMobileMenu" />
      <h1 class="title">{{ title }}</h1>
    </div>

    <div class="header-right">
      <!-- 👇 qui stampo i dati dell’utente corrente -->
      <!-- Mostra info utenti se disponibili -->


      <!-- Filtri per Desktop (v-if) -->
      <div v-if="isDesktop" class="header-controls">
        <DropdownButton>
          <template #icon>
            <FilterIcon />
          </template>
          <template #text>Strategy</template>
          <template #content>
            <StrategyFilter />
          </template>
        </DropdownButton>
        <DropdownButton>
          <template #icon>
            <CalendarIcon />
          </template>
          <template #text>Date Range</template>
          <template #content>
            <DateRangeFilter />
          </template>
        </DropdownButton>
      </div>

      <!-- Filtro unificato per Mobile (v-else) -->
      <div v-else class="header-controls">
        <DropdownButton>
          <template #icon>
            <FilterIcon />
          </template>
          <template #text>Filters</template>
          <template #content>
            <div class="mobile-filters">
              <StrategyFilter />
              <DateRangeFilter />
            </div>
          </template>
        </DropdownButton>
      </div>

      <BaseButton v-if="authStore.isAuthenticated" variant="secondary" size="small" @click="authStore.logout">
        Logout
      </BaseButton>
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--semantic-size-stack-md);
}

.header-left,
.header-right,
.header-controls {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

.title {
  font: var(--semantic-font-style-heading-2xl);
  color: var(--semantic-color-text-primary);
}

.users-info {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  margin-right: var(--semantic-size-stack-md);
}

.mobile-filters {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.hamburger-menu {
  display: none;
}

@media (max-width: 768px) {
  .hamburger-menu {
    display: flex;
  }

  .title {
    font: var(--semantic-font-style-heading-xl);
  }
}
</style>
