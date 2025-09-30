<template>
  <div class="rule-creator">
    <div class="col-rule">
      <span class="drag-handle-placeholder"></span>
      <BaseInput
        v-model="ruleText"
        placeholder="Enter rule description..."
        ref="inputRef"
        @keyup.enter="onSave"
        @keyup.esc="onCancel"
      />
    </div>
    <div class="col-metric-placeholder"></div>
    <div class="col-metric-placeholder"></div>
    <div class="col-metric-placeholder"></div>
    <div class="col-metric-placeholder"></div>
    <div class="col-action">
      <div class="actions">
        <BaseButton @click="onSave" size="small" :disabled="!ruleText.trim()">Save</BaseButton>
        <BaseButton @click="onCancel" size="small" variant="secondary">Cancel</BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps } from 'vue';
import { useRoute } from 'vue-router';
import { usePlaybookStore } from '@/stores/playbookStore';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const props = defineProps({
  groupId: {
    type: String,
    required: true,
  },
});

const store = usePlaybookStore();
const route = useRoute();

const ruleText = ref('');
const inputRef = ref(null);

const onSave = async () => {
  if (!ruleText.value.trim()) return;

  await store.createRule({
    playbookId: route.params.id,
    groupId: props.groupId,
    rule: ruleText.value,
  });

  // The store action will refresh the list, and we hide the creator
  store.setCreatingRuleInGroup(null);
};

const onCancel = () => {
  store.setCreatingRuleInGroup(null);
};

onMounted(() => {
  inputRef.value?.focus();
});
</script>

<style scoped>
.rule-creator {
  display: grid;
  grid-template-columns: minmax(0, 3fr) repeat(4, minmax(0, 1fr)) auto;
  gap: 1rem;
  align-items: center;
  padding: 0.75rem var(--semantic-size-inset-lg);
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.col-rule {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.drag-handle-placeholder {
  width: 14px; /* Match the width of the real drag handle */
}

.actions {
    display: flex;
    gap: 0.5rem;
}
</style>