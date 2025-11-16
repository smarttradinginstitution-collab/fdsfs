<template>
  <div class="conditions-block p-4 border rounded-md">
    <h3 class="text-lg font-semibold mb-2">Conditions</h3>
    <div v-if="conditions.length === 0" class="text-gray-500">
      No conditions defined for this playbook.
    </div>
    <ul v-else class="space-y-2">
      <li v-for="(condition, index) in conditions" :key="index" class="p-2 border rounded bg-gray-50">
        <span class="font-mono">{{ condition.variable }} {{ condition.operator }} {{ condition.value.value || `${condition.value.min} - ${condition.value.max}` }}</span>
        <span class="text-sm text-gray-600 ml-2">({{ condition.category }})</span>
      </li>
    </ul>
    <!-- Future implementation will include editing and reordering -->
  </div>
</template>

<script setup>
defineProps({
  conditions: {
    type: Array,
    default: () => [],
  },
});
</script>
