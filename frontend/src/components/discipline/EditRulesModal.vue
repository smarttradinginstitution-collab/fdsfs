<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title">Edit Rules</h3>
        <button @click="close" class="close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <div class="rules-form">
          <p class="form-description">
            Changes you make will only update your scoring for today and for future days.
          </p>

          <!-- Automated Rules -->
          <div class="form-section">
            <h4 class="section-title">Automated Rules</h4>
            <div class="rule-item" v-for="rule in automatedRules" :key="rule.id">
              <label :for="`rule-${rule.id}`">{{ rule.name }}</label>
              <!-- Different input types based on rule condition -->
              <div class="input-group">
                <input v-if="rule.condition_type === 'TIME'" type="time" v-model="rule.condition_value.time" class="form-input">

                <template v-if="rule.condition_type === 'PERCENTAGE_OR_FIXED'">
                  <input type="number" v-model="rule.condition_value.amount" class="form-input">
                  <select v-model="rule.condition_value.type" class="form-select">
                    <option value="FIXED_AMOUNT">$</option>
                    <option value="PERCENTAGE">%</option>
                  </select>
                </template>

                <input v-if="rule.condition_type === 'FIXED_AMOUNT'" type="number" v-model="rule.condition_value.amount" class="form-input">
                <input v-if="rule.condition_type === 'PERCENTAGE'" type="number" v-model="rule.condition_value.percentage" class="form-input">
              </div>
            </div>
          </div>

          <!-- Manual Rules -->
          <div class="form-section">
            <div class="section-header">
              <h4 class="section-title">Manual Rules</h4>
              <BaseButton @click="addManualRule" variant="tertiary" size="small">+ Add manual rule</BaseButton>
            </div>
            <div class="rule-item manual-rule" v-for="rule in manualRules" :key="rule.id">
              <input type="text" v-model="rule.name" placeholder="Rule name" class="form-input flex-grow">
              <BaseMultiSelect
                :options="dayOptions"
                v-model="rule.active_days"
                placeholder="Select days"
                class="day-selector"
              />
              <button @click="removeManualRule(rule.id)" class="delete-btn">&times;</button>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <BaseButton @click="close" variant="secondary" size="medium">Cancel</BaseButton>
        <BaseButton @click="save" variant="primary" size="medium">Save Changes</BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useDisciplineStore } from '@/stores/disciplineStore';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseMultiSelect from '@/components/ui/BaseMultiSelect.vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['close']);

const disciplineStore = useDisciplineStore();

// Local state for editing
const localRules = ref([]);

const automatedRules = computed(() => localRules.value.filter(r => r.rule_type === 'AUTOMATED'));
const manualRules = computed(() => localRules.value.filter(r => r.rule_type === 'MANUAL'));

// Watch for the modal opening to clone the rules from the store
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    // Deep clone to prevent modifying the store directly
    localRules.value = JSON.parse(JSON.stringify(disciplineStore.disciplineRules));
  }
});

function addManualRule() {
  localRules.value.push({
    rule_type: 'MANUAL',
    name: '',
    description: '',
    condition_type: null,
    condition_value: {},
    active_days: [0, 1, 2, 3, 4], // Default to Mon-Fri
    id: `new-${Date.now()}` // Temporary ID for v-for key
  });
}

function removeManualRule(ruleId) {
    const index = localRules.value.findIndex(r => r.id === ruleId);
    if (index > -1) {
        localRules.value.splice(index, 1);
    }
}

function close() {
  emit('close');
}

async function save() {
  try {
    // Filter out temporary IDs before sending to backend
    const rulesToSave = localRules.value.map(rule => {
      if (String(rule.id).startsWith('new-')) {
        const { id, ...rest } = rule;
        return rest;
      }
      return rule;
    });

    await disciplineStore.bulkUpdateDisciplineRules(rulesToSave);
    emit('close');
  } catch (error) {
    console.error("Failed to save rules:", error);
    // Optionally show an error message to the user
  }
}

const dayOptions = [
  { value: 0, text: 'Mon' }, { value: 1, text: 'Tue' }, { value: 2, text: 'Wed' },
  { value: 3, text: 'Thu' }, { value: 4, text: 'Fri' }, { value: 5, text: 'Sat' },
  { value: 6, text: 'Sun' }
];

</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--semantic-color-overlay-background);
  display: grid;
  place-items: center;
  z-index: var(--semantic-layer-z-index-modal);
}

.modal-content {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-component-modal-padding-desktop);
  width: 90%;
  max-width: var(--semantic-size-component-modal-max-width-desktop);
  box-shadow: var(--semantic-effect-shadow-elevation-high);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--semantic-size-component-modal-gap-desktop);
}

.modal-title {
  font: var(--semantic-font-style-heading-lg);
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: var(--semantic-color-text-secondary);
}

.modal-body {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 1rem; /* for scrollbar */
}

.rules-form {
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-lg);
}

.form-description {
    font: var(--semantic-font-style-body-sm);
    color: var(--semantic-color-text-secondary);
    background-color: var(--semantic-color-surface-secondary);
    padding: var(--semantic-size-inset-md);
    border-radius: var(--semantic-border-radius-actions);
}

.form-section {
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-md);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.section-title {
    font: var(--semantic-font-style-heading-sm);
    color: var(--semantic-color-text-primary);
}

.rule-item {
    display: flex;
    align-items: center;
    gap: var(--semantic-size-stack-md);
}

.rule-item label {
    flex-basis: 200px;
    font: var(--semantic-font-style-body-base);
}

.input-group {
    display: flex;
    align-items: center;
    gap: var(--semantic-size-stack-xs);
}

.form-input {
    /* Assuming a base style for inputs exists or define here */
    padding: var(--semantic-size-inset-sm);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-actions);
    background-color: var(--semantic-color-surface-primary);
    color: var(--semantic-color-text-primary);
    width: 150px;
}

.form-select {
    padding: var(--semantic-size-inset-sm);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-actions);
    background-color: var(--semantic-color-surface-primary);
    color: var(--semantic-color-text-primary);
}

.manual-rule {
    gap: var(--semantic-size-stack-sm);
}

.flex-grow {
    flex-grow: 1;
}

.day-selector {
    width: 250px;
}

.delete-btn {
    background: none;
    border: 1px solid var(--semantic-color-border-subtle);
    color: var(--semantic-color-text-secondary);
    border-radius: 50%;
    width: 24px;
    height: 24px;
    cursor: pointer;
    display: grid;
    place-items: center;
    font-size: 1.2rem;
}

.delete-btn:hover {
    background-color: var(--semantic-color-surface-hover);
    color: var(--semantic-color-feedback-negative-text);
}


.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
  margin-top: var(--semantic-size-component-modal-gap-desktop);
}
</style>