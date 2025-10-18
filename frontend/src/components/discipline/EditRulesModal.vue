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

          <!-- Global Settings for Automated Rules -->
          <div class="form-section">
             <h4 class="section-title">Global Settings</h4>
             <div class="rule-item">
                <label for="trading-days">Trading days</label>
                <BaseMultiSelect
                    :options="dayOptions"
                    v-model="globalTradingDays"
                    placeholder="Select days"
                    class="day-selector"
                />
             </div>
          </div>

          <!-- Automated Rules Parameters -->
          <div class="form-section">
            <h4 class="section-title">Parameters</h4>

            <!-- Start my day by -->
            <div class="rule-item" v-if="startMyDayRule.condition_value">
              <label for="start-day">Start my day by</label>
              <input id="start-day" type="time" v-model="startMyDayRule.condition_value.time" class="form-input">
            </div>

            <!-- Link trades to playbook -->
            <div class="rule-item" v-if="linkTradesRule.condition_value">
              <label for="link-trades">Link trades to playbook</label>
              <div class="input-group">
                <input id="link-trades" type="number" v-model="linkTradesRule.condition_value.percentage" class="form-input short-input">
                <span class="input-adornment">%</span>
              </div>
            </div>

            <!-- Trade has stop loss -->
            <div class="rule-item" v-if="stopLossRule.condition_value">
              <label for="stop-loss">Trade has stop loss</label>
              <div class="input-group">
                <input id="stop-loss" type="number" v-model="stopLossRule.condition_value.percentage" class="form-input short-input">
                <span class="input-adornment">%</span>
              </div>
            </div>

            <!-- Max loss per trade -->
            <div class="rule-item" v-if="maxLossPerTradeRule.condition_value">
              <label for="max-loss-trade">Max loss per trade</label>
              <div class="input-group">
                <input id="max-loss-trade" type="number" v-model="maxLossPerTradeRule.condition_value.amount" class="form-input">
                <select v-model="maxLossPerTradeRule.condition_type" class="form-select">
                  <option value="FIXED_AMOUNT">$</option>
                  <option value="PERCENTAGE">%</option>
                </select>
              </div>
            </div>

            <!-- Max loss per day -->
            <div class="rule-item" v-if="maxLossPerDayRule.condition_value">
              <label for="max-loss-day">Max loss per day</label>
              <div class="input-group">
                <span class="input-adornment">$</span>
                <input id="max-loss-day" type="number" v-model="maxLossPerDayRule.condition_value.amount" class="form-input">
              </div>
            </div>

          </div>

          <!-- Manual Rules -->
          <div class="form-section">
            <div class="section-header">
              <h4 class="section-title">Manual Rules</h4>
              <BaseButton @click="addManualRule" variant="tertiary" size="small">+ Add manual rule</BaseButton>
            </div>
            <div v-if="manualRules.length === 0" class="empty-state">
                No manual rules defined. Add one to get started.
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

const manualRules = computed(() => localRules.value.filter(r => r.rule_type === 'MANUAL'));

// Specific computed properties for each automated rule
const findRule = (name) => computed(() => localRules.value.find(r => r.name === name) || {});
const startMyDayRule = findRule("Start my day by 12:00");
const linkTradesRule = findRule("Link trades to playbook");
const stopLossRule = findRule("Trade has stop loss");
const maxLossPerTradeRule = findRule("Max loss per trade");
const maxLossPerDayRule = findRule("Max loss per day");

const globalTradingDays = computed({
  get() {
    // Return the active_days from the first automated rule as a representative
    const firstAutoRule = localRules.value.find(r => r.rule_type === 'AUTOMATED');
    return firstAutoRule ? firstAutoRule.active_days : [];
  },
  set(newDays) {
    // Update active_days for all automated rules
    localRules.value.forEach(rule => {
      if (rule.rule_type === 'AUTOMATED') {
        rule.active_days = newDays;
      }
    });
  }
});

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
    padding: var(--semantic-size-inset-lg);
}

.rules-form {
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-xl);
}

.form-description {
    font: var(--semantic-font-style-body-sm);
    color: var(--semantic-color-text-secondary);
    background-color: var(--semantic-color-surface-secondary);
    padding: var(--semantic-size-inset-md);
    border-radius: var(--semantic-border-radius-actions);
    border: 1px solid var(--semantic-color-border-subtle);
}

.form-section {
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-lg);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--semantic-color-border-subtle);
    padding-bottom: var(--semantic-size-stack-sm);
}

.section-title {
    font: var(--semantic-font-style-heading-md);
    color: var(--semantic-color-text-primary);
}

.rule-item {
    display: grid;
    grid-template-columns: 250px 1fr;
    align-items: center;
    gap: var(--semantic-size-stack-lg);
}

.rule-item label {
    font: var(--semantic-font-style-body-base);
    color: var(--semantic-color-text-secondary);
    text-align: right;
}

.input-group {
    display: flex;
    align-items: center;
    gap: var(--semantic-size-stack-xs);
    width: fit-content;
}

.form-input {
    padding: var(--semantic-size-inset-sm);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-actions);
    background-color: var(--semantic-color-surface-primary);
    color: var(--semantic-color-text-primary);
    width: 200px;
}

.form-input.short-input {
    width: 100px;
}

.form-select {
    padding: var(--semantic-size-inset-sm);
    height: 100%;
    border: 1px solid var(--semantic-color-border-default);
    border-left: none;
    border-radius: 0 var(--semantic-border-radius-actions) var(--semantic-border-radius-actions) 0;
    background-color: var(--semantic-color-surface-secondary);
    color: var(--semantic-color-text-primary);
}
.input-group .form-input {
    border-right: none;
    border-radius: var(--semantic-border-radius-actions) 0 0 var(--semantic-border-radius-actions);
}


.input-adornment {
    padding: var(--semantic-size-inset-sm);
    background-color: var(--semantic-color-surface-secondary);
    border: 1px solid var(--semantic-color-border-default);
    border-left: none;
    color: var(--semantic-color-text-secondary);
    border-radius: 0 var(--semantic-border-radius-actions) var(--semantic-border-radius-actions) 0;
}
.input-group .form-input.short-input {
     border-radius: var(--semantic-border-radius-actions) 0 0 var(--semantic-border-radius-actions);
}

.manual-rule {
    display: flex;
    gap: var(--semantic-size-stack-sm);
}

.flex-grow {
    flex-grow: 1;
}

.day-selector {
    width: 300px;
}

.empty-state {
    text-align: center;
    padding: var(--semantic-size-inset-xl);
    color: var(--semantic-color-text-secondary);
    font: var(--semantic-font-style-body-base);
    background-color: var(--semantic-color-surface-secondary);
    border-radius: var(--semantic-border-radius-surface);
}

.delete-btn {
    background: none;
    border: none;
    color: var(--semantic-color-text-secondary);
    cursor: pointer;
    font-size: 1.5rem;
    padding: 0 var(--semantic-size-inset-sm);
}

.delete-btn:hover {
    color: var(--semantic-color-feedback-negative-text);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
  margin-top: var(--semantic-size-component-modal-gap-desktop);
}
</style>