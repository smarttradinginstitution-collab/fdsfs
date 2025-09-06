<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AppSidebar from './AppSidebar.vue';
import DashboardHeader from './DashboardHeader.vue';
import { useUiStore } from '../../stores/uiStore';

const uiStore = useUiStore();
const route = useRoute();

const pageTitle = computed(() => route.meta.title || 'Trade Vantage');
</script>

<template>
  <div class="app-layout">
    <AppSidebar />

    <div class="content-wrapper" :class="{ 'sidebar-is-collapsed': uiStore.isSidebarCollapsed }">
      <header class="layout-header">
        <DashboardHeader :title="pageTitle" />
      </header>
      <main class="layout-main">
        <slot></slot> <!-- RouterView will be passed here -->
      </main>
    </div>

    <div
      v-if="uiStore.isMobileMenuOpen"
      class="mobile-menu-overlay"
      @click="uiStore.closeMobileMenu"
    ></div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  position: relative;
  min-height: 100vh;
  background-color: var(--semantic-color-surface-page);
}

.content-wrapper {
  flex-grow: 1;
  margin-left: var(--semantic-size-component-sidebar-width-expanded);
  transition: margin-left var(--semantic-animation-duration-complex) var(--semantic-animation-easing-exit);
  display: flex;
  flex-direction: column;
}

.content-wrapper.sidebar-is-collapsed {
  margin-left: var(--semantic-size-component-sidebar-width-collapsed);
}

.layout-header {
  background-color: var(--semantic-color-surface-primary);
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.layout-main {
  flex-grow: 1;
  padding: var(--semantic-size-inset-xl);
}

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
  .content-wrapper.sidebar-is-collapsed,
  .content-wrapper {
    margin-left: 0;
  }
}
</style>
