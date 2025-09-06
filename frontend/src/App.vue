<script setup>
import { computed, shallowRef } from 'vue';
import { useRoute } from 'vue-router';
import AppSidebar from './components/layout/AppSidebar.vue';
import DashboardHeader from './components/layout/DashboardHeader.vue';
import MainLayout from './components/layout/MainLayout.vue';
import AuthLayout from './components/layout/AuthLayout.vue';
import { useUiStore } from './stores/uiStore';

const uiStore = useUiStore();
const route = useRoute();

const pageTitle = computed(() => route.meta.title || 'Trade Vantage');

const layouts = {
  MainLayout,
  AuthLayout,
};

const layout = computed(() => {
  const layoutName = route.meta.layout || 'MainLayout';
  return layouts[layoutName] || MainLayout;
});
</script>

<template>
  <component :is="layout">
    <RouterView />
  </component>
</template>

<style>
/* Global styles can remain here, but layout-specific styles
   should be in their respective component files. */
</style>
