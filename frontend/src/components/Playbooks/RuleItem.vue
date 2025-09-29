<script setup>
import { ref, watch } from 'vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import CloseIcon from '@/components/icons/CloseIcon.vue';
import IconButton from '@/components/ui/IconButton.vue';

const props = defineProps({
  rule: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['update:rule', 'delete:rule']);

const localRule = ref(JSON.parse(JSON.stringify(props.rule)));

watch(localRule, (newRule) => {
  emit('update:rule', newRule);
}, { deep: true });

</script>

<template>
  <div class="rule-item">
    <BaseInput
      v-model="localRule.description"
      placeholder="Enter rule description..."
      maxlength="40"
      class="rule-input"
    />
    <IconButton @click="$emit('delete:rule')" class="delete-btn" aria-label="Delete rule">
        <CloseIcon />
    </IconButton>
  </div>
</template>

<style scoped>
.rule-item {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  width: 100%;
}

.rule-input {
  flex-grow: 1;
}

.delete-btn {
    color: var(--semantic-color-text-secondary);
}
.delete-btn:hover {
    color: var(--semantic-color-text-danger);
}
</style>