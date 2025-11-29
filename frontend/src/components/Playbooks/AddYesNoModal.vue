<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3 class="font-semibold">Add New Yes/No Rule</h3>
      <BaseInput
        v-model="ruleText"
        placeholder="Enter the rule description..."
        @keydown.enter="addRule"
      />
      <div class="modal-actions">
        <BaseButton @click="$emit('close')" variant="secondary">Cancel</BaseButton>
        <BaseButton @click="addRule" variant="primary">Add Rule</BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const emit = defineEmits(['close', 'add-rule']);
const ruleText = ref('');

const addRule = () => {
  if (ruleText.value.trim()) {
    emit('add-rule', ruleText.value);
  }
};
</script>
