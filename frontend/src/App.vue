<script setup>
import { computed, onMounted } from 'vue';
import { RouterView, useRoute } from 'vue-router';
import AppSidebar from './components/layout/AppSidebar.vue';
import DashboardHeader from './components/layout/DashboardHeader.vue';
import MainLayout from './components/layout/MainLayout.vue';
import ToastNotification from './components/ui/ToastNotification.vue';
import FullScreenLoader from './components/ui/FullScreenLoader.vue';
import ImageLightbox from './components/ui/ImageLightbox.vue';
import { useUiStore } from './stores/uiStore';

const uiStore = useUiStore();
const route = useRoute();

// Initialize the theme as soon as the app mounts
onMounted(() => {
  uiStore.initTheme();
});

const pageTitle = computed(() => route.meta.title || 'Trade Vantage');

// This computed property checks if the route is marked as public.
// Public routes (like login) will not use the main app layout.
const isPublicRoute = computed(() => route.meta.public);
const isFullScreenRoute = computed(() => route.meta.fullScreen);
</script>

<template>
  <!-- Render only the component for public routes -->
  <RouterView v-if="isPublicRoute" />

  <!-- Render a dedicated full-screen layout -->
  <div v-else-if="isFullScreenRoute" class="fullscreen-layout">
    <RouterView />
  </div>

  <!-- Render the full layout for protected routes -->
  <div v-else class="app-layout">
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

    <!-- Toast Notification -->
    <ToastNotification />
  </div>

  <!-- Global Full Screen Loader -->
  <FullScreenLoader v-if="uiStore.isAppLoading" :message="uiStore.loaderMessage" />

  <!-- Global Image Lightbox -->
  <ImageLightbox />
</template>

<style lang="scss">
.fullscreen-layout {
  min-height: 100vh;
  background-color: var(--semantic-color-surface-page);
}

.app-layout {
  display: flex;
  position: relative;
  min-height: 100vh;
  background-color: var(--semantic-color-surface-page);
}

.content-wrapper {
  flex-grow: 1;
  min-width: 0; /* Prevents the container from overflowing when its content is too wide */
  /*
    BEST PRACTICE: Layout con Sidebar Fissa
    La sidebar ha `position: fixed`, quindi è rimossa dal flusso del layout.
    Per evitare che il contenuto principale finisca sotto la sidebar, applichiamo
    un `margin-left` al content-wrapper. Questo margine è uguale alla larghezza
    della sidebar, creando lo spazio necessario.
    Usiamo i token per la larghezza della sidebar per mantenere tutto sincronizzato.
  */
  margin-left: var(--semantic-size-component-sidebar-width-expanded);
  transition: margin-left var(--semantic-animation-duration-complex) var(--semantic-animation-easing-exit);
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

@include media-down('md') {
  /* Aumentata la specificità per sovrascrivere lo stato collassato su mobile */
  .content-wrapper.sidebar-is-collapsed,
  .content-wrapper {
    margin-left: 0;
  }
}
</style>
