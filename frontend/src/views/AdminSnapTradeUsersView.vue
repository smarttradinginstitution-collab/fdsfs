<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import BaseTable from '@/components/ui/BaseTable.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';

const users = ref([]);
const isLoading = ref(true);
const error = ref(null);

const tableHeaders = [
  { key: 'userId', text: 'SnapTrade User ID' },
];

onMounted(async () => {
  try {
    const response = await apiClient.get('/api/v1/admin/snaptrade-users');
    users.value = response.data.map(userId => ({ userId }));
  } catch (err) {
    error.value = 'Failed to fetch SnapTrade users.';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div class="p-4 sm:p-6">
    <h1 class="text-2xl font-bold mb-4">Admin - SnapTrade Users</h1>
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <LoadingSpinner />
    </div>
    <div v-else-if="error" class="text-red-500 bg-red-100 p-4 rounded-md">
      {{ error }}
    </div>
    <div v-else>
      <BaseTable :headers="tableHeaders" :items="users" />
    </div>
  </div>
</template>
