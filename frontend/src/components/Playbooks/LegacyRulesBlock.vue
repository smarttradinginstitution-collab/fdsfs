<template>
  <div class="legacy-rules-block p-4 border rounded-md bg-gray-100">
    <h3 class="text-lg font-semibold mb-2 text-gray-700">Legacy Rules (Read-Only)</h3>
    <div v-if="!content || Object.keys(content).length === 0" class="text-gray-500">
      No legacy rules found.
    </div>
    <div v-else>
      <div v-for="(rules, groupName) in content" :key="groupName" class="mb-3">
        <h4 class="font-semibold text-gray-600">{{ groupName }}</h4>
        <ul class="list-disc list-inside ml-4">
          <li v-for="(rule, index) in rules" :key="index" class="text-gray-800">{{ rule }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  content: {
    type: Object,
    default: () => ({}),
  },
});
</script>
