<template>
  <div class="page-container">
    <!-- PAGE HEADER -->
    <div class="header">
      <div class="header-content">
        <h1 class="page-title">Tags</h1>
        <p class="page-subtitle">Manage your tags and analyze their performance.</p>
      </div>
      <BaseButton @click="store.setCreatingGroup(true)" v-if="activeTab === 'manage' && !store.isCreatingGroup">
        <PlusIcon class="w-4 h-4 mr-2" />
        Add Group
      </BaseButton>
    </div>

    <!-- TABS -->
    <BaseTabs v-model="activeTab" :tabs="tabs" />

    <!-- TAB CONTENT -->
    <div class="tab-content">
      <TagManagementTab v-if="activeTab === 'manage'" />
      <TagReportTab v-if="activeTab === 'report'" />
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useTagsStore } from '@/stores/tagsStore';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseTabs from '@/components/ui/BaseTabs.vue';
import TagManagementTab from '@/components/tags/TagManagementTab.vue';
import TagReportTab from '@/components/tags/TagReportTab.vue';
import { PlusIcon } from '@heroicons/vue/24/solid';

const store = useTagsStore();
const activeTab = ref('manage');

const tabs = [
  { id: 'manage', label: 'Tag Management' },
  { id: 'report', label: 'Performance Report' },
];
</script>

<style scoped>
.page-container {
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.page-title {
  font: var(--semantic-font-style-heading-2xl);
}
.page-subtitle {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-secondary);
  margin-top: var(--semantic-size-stack-xxs);
}
.tab-content {
  margin-top: var(--semantic-size-stack-lg);
}
</style>