
<script setup>
import { ref, watch, computed } from 'vue';
import { usePlaybookStore } from '@/stores/playbookStore';
import { useRoute } from 'vue-router';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseSelect from '@/components/ui/BaseSelect.vue';
import TrashIcon from '@/components/icons/TrashIcon.vue';
import IconButton from '@/components/ui/IconButton.vue';

const props = defineProps({
  conditions: {
    type: Array,
    default: () => [],
  },
});

const route = useRoute();
const playbookStore = usePlaybookStore();
const playbookId = computed(() => route.params.id);

const localConditions = ref([...props.conditions]);

const newCondition = ref({
  variable: '',
  operator: 'EQUALS',
  value: { type: 'VALUE', value: '' },
  category: 'TECHNICAL',
});

const operatorOptions = [
  { value: 'EQUALS', label: 'Equals' },
  { value: 'NOT_EQUALS', label: 'Not Equals' },
  { value: 'GREATER_THAN', label: 'Greater Than' },
  { value: 'LESS_THAN', label: 'Less Than' },
  { value: 'IN_RANGE', label: 'In Range' },
];

const categoryOptions = [
    { value: 'TECHNICAL', label: 'Technical' },
    { value: 'FUNDAMENTAL', label: 'Fundamental' },
    { value: 'SENTIMENT', label: 'Sentiment' },
    { value: 'CUSTOM', label: 'Custom' },
];

watch(() => props.conditions, (newVal) => {
  localConditions.value = [...newVal];
}, { deep: true });

const addCondition = () => {
  if (!newCondition.value.variable || !newCondition.value.value.value) {
    // Basic validation
    return;
  }
  const conditionToAdd = {
    ...newCondition.value,
    id: `temp-${Date.now()}` // Temporary ID for list key
  };
  localConditions.value.push(conditionToAdd);
  saveConditions();

  // Reset form
  newCondition.value = {
    variable: '',
    operator: 'EQUALS',
    value: { type: 'VALUE', value: '' },
    category: 'TECHNICAL',
  };
};

const removeCondition = (index) => {
  localConditions.value.splice(index, 1);
  saveConditions();
};

const saveConditions = async () => {
    try {
        const conditionsToSave = localConditions.value.map(({ id, ...rest }) => rest);
        await playbookStore.updatePlaybookConditions({
            playbookId: playbookId.value,
            conditions: conditionsToSave,
        });
    } catch (error) {
        console.error('Failed to save conditions:', error);
        // Optionally, show an error message to the user
    }
};
</script>

<template>
  <div class="conditions-block">
    <h3 class="block-title">Conditions</h3>

    <!-- List of existing conditions -->
    <div v-if="localConditions.length === 0" class="no-items-message">
      No conditions defined for this playbook.
    </div>
    <ul v-else class="items-list">
      <li v-for="(condition, index) in localConditions" :key="condition.id || index" class="list-item">
        <span class="condition-text">
          <span class="variable">{{ condition.variable }}</span>
          <span class="operator">{{ condition.operator }}</span>
          <span class="value">{{ condition.value.value }}</span>
        </span>
        <IconButton @click="removeCondition(index)" ariaLabel="Delete condition">
            <TrashIcon />
        </IconButton>
      </li>
    </ul>

    <!-- Form to add a new condition -->
    <div class="add-item-form">
      <h4 class="form-title">Add New Condition</h4>
      <div class="form-row">
        <BaseInput
          v-model="newCondition.variable"
          label="Variable"
          placeholder="e.g., 'RSI'"
          class="form-field"
        />
        <BaseSelect
          v-model="newCondition.operator"
          :options="operatorOptions"
          label="Operator"
          class="form-field"
        />
        <BaseInput
          v-model="newCondition.value.value"
          label="Value"
          placeholder="e.g., '70'"
          class="form-field"
        />
        <BaseSelect
          v-model="newCondition.category"
          :options="categoryOptions"
          label="Category"
          class="form-field"
        />
      </div>
      <BaseButton @click="addCondition" variant="primary" class="add-button">Add Condition</BaseButton>
    </div>
  </div>
</template>

<style scoped>
.conditions-block {
  padding: var(--semantic-size-inset-md);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
}

.block-title {
  font: var(--semantic-font-style-body-lg-bold);
  margin-bottom: var(--semantic-size-stack-md);
}

.no-items-message {
  color: var(--semantic-color-text-subtle);
  padding: var(--semantic-size-inset-lg);
  text-align: center;
  border: 2px dashed var(--semantic-color-border-subtle);
  border-radius: var(--semantic-border-radius-surface);
  margin-bottom: var(--semantic-size-stack-md);
}

.items-list {
  list-style: none;
  padding: 0;
  margin-bottom: var(--semantic-size-stack-lg);
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-element);
  background-color: var(--semantic-color-surface-sunken);
  margin-bottom: var(--semantic-size-stack-sm);
}

.condition-text {
  font-family: monospace;
  font-size: 0.9rem;
  display: flex;
  gap: var(--semantic-size-inline-md);
}

.variable { color: var(--semantic-color-text-primary); }
.operator { color: var(--semantic-color-text-subtle); }
.value { color: var(--semantic-color-text-accent); }

.add-item-form {
  border-top: 1px solid var(--semantic-color-border-default);
  padding-top: var(--semantic-size-stack-md);
}

.form-title {
  font: var(--semantic-font-style-body-md-bold);
  margin-bottom: var(--semantic-size-stack-md);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--semantic-size-stack-md);
  margin-bottom: var(--semantic-size-stack-md);
}

.form-field {
  width: 100%;
}

.add-button {
  display: block;
  margin-left: auto;
}
</style>
