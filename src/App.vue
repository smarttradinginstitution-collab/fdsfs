<script setup>
import { computed } from 'vue';
import { RouterView, useRoute } from 'vue-router';
import AppSidebar from './components/layout/AppSidebar.vue';
import DashboardHeader from './components/layout/DashboardHeader.vue';
import MainLayout from './components/layout/MainLayout.vue'; // Importato MainLayout
import { useUiStore } from './stores/uiStore';

const uiStore = useUiStore();
const route = useRoute();

const pageTitle = computed(() => route.meta.title || 'Trade Vantage');
</script>

<template>
  <div class="app-layout">
    <AppSidebar />

    <div class="content-wrapper" :class="{ 'sidebar-is-collapsed': uiStore.isSidebarCollapsed }">
      <MainLayout>
        <template #header>
          <DashboardHeader :title="pageTitle" />
        </template>
        <template #main>
          <RouterView />
        </template>
      </MainLayout>
    </div>

    <div
      v-if="uiStore.isMobileMenuOpen"
      class="mobile-menu-overlay"
      @click="uiStore.closeMobileMenu"
    ></div>
  </div>
</template>

<style>
.app-layout {
  display: flex;
  position: relative;
  min-height: 100vh;
  background-color: var(--semantic-color-surface-page);
}

.content-wrapper {
  flex-grow: 1; /* Mantenuto per occupare lo spazio */
  margin-left: var(--semantic-size-component-sidebar-width-expanded);
  transition: margin-left var(--semantic-animation-duration-complex) var(--semantic-animation-easing-exit);
  /* 'display: flex' rimosso per evitare conflitti di layout */
}

.content-wrapper.sidebar-is-collapsed {
  margin-left: var(--semantic-size-component-sidebar-width-collapsed);
}

/* .main-content rimosso perché la sua logica è ora in MainLayout.vue */

.mobile-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: var(--semantic-layer-z-index-overlay);
}

@media (max-width: 768px) {
  /* Aumentata la specificità per sovrascrivere lo stato collassato su mobile */
  .content-wrapper.sidebar-is-collapsed,
  .content-wrapper {
    margin-left: 0;
  }
}
</style>
