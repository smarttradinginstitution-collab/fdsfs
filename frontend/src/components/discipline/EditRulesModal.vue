<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title">Rules</h3>
        <button @click="close" class="close-btn">&times;</button>
      </div>

      <div class="modal-body">
        <div class="info-note">
          Changes you make will only update your scoring for today and for future days.
        </div>

        <!-- Trading Days -->
        <div class="rule-row">
          <div class="rule-label">
            <h4>Trading days</h4>
            <p>The days on which these rules should be active.</p>
          </div>
          <div class="rule-control">
            <div class="day-selector">
              <button
                v-for="(day, index) in weekDays"
                :key="day"
                :class="{ active: localSettings.trading_days.includes(index + 1) }"
                @click="toggleDay(index + 1)"
              >
                {{ day }}
              </button>
            </div>
          </div>
        </div>

        <!-- Automated Rules -->
        <div class="rule-row">
          <div class="rule-label">
            <h4>Start my day by</h4>
            <p>The time you should start your day by and enter your starting journal entry before your trading session.</p>
          </div>
          <div class="rule-control">
            <BaseInput type="time" v-model="localSettings.start_day_by" />
          </div>
        </div>

        <div class="rule-row">
          <div class="rule-label">
            <h4>Link trades to playbook</h4>
            <p>The percentage of trades opened on a day that are linked to a playbook.</p>
          </div>
          <div class="rule-control">
            <BaseInput type="number" v-model.number="localSettings.link_trades_to_playbook_threshold" addon-after="%" />
          </div>
        </div>

        <div class="rule-row">
          <div class="rule-label">
            <h4>Trade has stop loss</h4>
            <p>The percentage of trades opened on a day that have a stop loss added.</p>
          </div>
          <div class="rule-control">
            <BaseInput type="number" v-model.number="localSettings.trade_has_stop_loss_threshold" addon-after="%" />
          </div>
        </div>

        <div class="rule-row">
          <div class="rule-label">
            <h4>Max loss per trade</h4>
            <p>The maximum loss on a trade in amount or in percentage of the trade's account balance.</p>
          </div>
          <div class="rule-control-group">
            <div class="tabs">
              <button :class="{ active: localSettings.max_loss_per_trade_type === '%' }" @click="localSettings.max_loss_per_trade_type = '%'">%</button>
              <button :class="{ active: localSettings.max_loss_per_trade_type === '$' }" @click="localSettings.max_loss_per_trade_type = '$'">$</button>
            </div>
            <BaseInput type="number" v-model.number="localSettings.max_loss_per_trade_value" />
          </div>
        </div>

        <div class="rule-row">
          <div class="rule-label">
            <h4>Max loss per day</h4>
            <p>The maximum loss on a day among all accounts.</p>
          </div>
          <div class="rule-control">
            <BaseInput type="number" v-model.number="localSettings.max_loss_per_day" addon-before="$" />
          </div>
        </div>

        <!-- Manual Rules -->
        <div class="manual-rules-section">
          <div class="manual-rules-header">
            <h4>MANUAL RULES</h4>
            <BaseButton variant="secondary" size="small" @click="addManualRule">+ Add manual rule</BaseButton>
          </div>
          <p class="subtitle">The rule will be added as a daily check list</p>

          <div v-for="(rule, index) in localManualRules" :key="index" class="manual-rule-row">
            <BaseInput type="text" v-model="rule.name" placeholder="Rule name" />
            <BaseSelect
              :model-value="JSON.stringify(rule.frequency)"
              @update:model-value="rule.frequency = JSON.parse($event)"
              :options="frequencyOptions"
            />
            <button @click="removeManualRule(index)" class="delete-rule-btn">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <BaseButton @click="close" variant="secondary" size="medium">Cancel</BaseButton>
        <BaseButton @click="save" variant="primary" size="medium" :loading="disciplineStore.isLoading">Save Changes</BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { useDisciplineStore } from '@/stores/disciplineStore';
import BaseButton from '@/components/ui/BaseButton.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseSelect from '@/components/ui/BaseSelect.vue';
import { cloneDeep } from 'lodash';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['close', 'save']);

const disciplineStore = useDisciplineStore();

const localSettings = ref({});
const localManualRules = ref([]);

const weekDays = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
const frequencyOptions = [
  { value: JSON.stringify([1, 2, 3, 4, 5]), text: 'Mon-Fri' },
  { value: JSON.stringify([6, 7]), text: 'Sat-Sun' },
  { value: JSON.stringify([1, 2, 3, 4, 5, 6, 7]), text: 'Daily' },
];

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    document.body.classList.add('modal-open');
    // Deep clone the store state to local state for editing
    localSettings.value = cloneDeep(disciplineStore.settings || {
        trading_days: [1, 2, 3, 4, 5],
        start_day_by: '09:30',
        link_trades_to_playbook_threshold: 100,
        trade_has_stop_loss_threshold: 100,
        max_loss_per_trade_type: '$',
        max_loss_per_trade_value: 500,
        max_loss_per_day: 2000,
    });
    localManualRules.value = cloneDeep(disciplineStore.manualRules);
  } else {
    document.body.classList.remove('modal-open');
  }
});

// Ensure the class is removed if the component is unmounted while open
onUnmounted(() => {
    document.body.classList.remove('modal-open');
});

function toggleDay(day) {
  const index = localSettings.value.trading_days.indexOf(day);
  if (index > -1) {
    localSettings.value.trading_days.splice(index, 1);
  } else {
    localSettings.value.trading_days.push(day);
  }
}

function addManualRule() {
  localManualRules.value.push({ name: '', frequency: [1, 2, 3, 4, 5] });
}

function removeManualRule(index) {
  localManualRules.value.splice(index, 1);
}

function close() {
  emit('close');
}

async function save() {
  await disciplineStore.saveDisciplineSettings(localSettings.value);

  // Basic diffing for manual rules to avoid deleting and recreating all
  const originalRules = disciplineStore.manualRules;
  const newRules = localManualRules.value;

  // Rules to delete
  for (const oldRule of originalRules) {
      if (!newRules.some(newRule => newRule.id === oldRule.id)) {
          await disciplineStore.deleteManualRule(oldRule.id);
      }
  }

  // Rules to add or update
  for (const newRule of newRules) {
      if (!newRule.id) {
          // Add new rule
          await disciplineStore.addManualRule({ name: newRule.name, frequency: newRule.frequency });
      } else {
          // Check if rule has changed before updating
          const oldRule = originalRules.find(r => r.id === newRule.id);
          if (oldRule.name !== newRule.name || JSON.stringify(oldRule.frequency) !== JSON.stringify(newRule.frequency)) {
              await disciplineStore.updateManualRule(newRule.id, { name: newRule.name, frequency: newRule.frequency });
          }
      }
  }

  emit('save');
  close();
}

</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: grid;
  place-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #2a2a3e;
  border-radius: 8px;
  padding: 20px; /* Reduced padding */
  width: 90%;
  max-width: 700px; /* Increased width */
  box-shadow: 0 4px_6px rgba(0, 0, 0, 0.1);
  color: #fff;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #9a9a9a;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px; /* Reduced gap */
}

.info-note {
  background-color: #31314a;
  padding: 10px; /* Reduced padding */
  border-radius: 6px;
  font-size: 13px; /* Slightly smaller font */
  text-align: center;
  margin-bottom: 8px; /* Reduced margin */
}

.rule-row, .rule-control-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px; /* Reduced gap */
}

.rule-label {
  flex: 1;
}
.rule-label h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
}
.rule-label p {
  margin: 0;
  font-size: 12px;
  color: #9a9a9a;
}

.rule-control {
  min-width: 150px;
}

.rule-control-group {
    display: flex;
    align-items: stretch;
    min-width: 150px;
}

.day-selector {
  display: flex;
  gap: 5px;
}
.day-selector button {
  background-color: #31314a;
  border: 1px solid #4a4a6a;
  color: #fff;
  border-radius: 4px;
  padding: 6px 10px; /* Reduced padding */
  font-size: 12px; /* Smaller font */
  cursor: pointer;
  transition: background-color 0.2s;
}
.day-selector button.active {
  background-color: #5a5a8a;
  border-color: #7a7ab8;
}

.tabs {
    display: flex;
    border: 1px solid #4a4a6a;
    border-radius: 6px 0 0 6px;
    overflow: hidden;
}
.tabs button {
    background-color: #31314a;
    border: none;
    color: #fff;
    padding: 6px 10px; /* Reduced padding */
    font-size: 12px; /* Smaller font */
    cursor: pointer;
}
.tabs button.active {
    background-color: #5a5a8a;
}
.tabs button:first-child {
    border-right: 1px solid #4a4a6a;
}

.rule-control-group .BaseInput {
    border-radius: 0 6px 6px 0;
}

.manual-rules-section {
  border-top: 1px solid #4a4a6a;
  padding-top: 20px;
}

.manual-rules-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.manual-rules-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 12px;
  color: #9a9a9a;
  margin: 4px 0 16px 0;
}

.manual-rule-row {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}
.manual-rule-row .BaseInput {
  flex-grow: 1;
}

.delete-rule-btn {
  background: none;
  border: none;
  color: #9a9a9a;
  cursor: pointer;
  font-size: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #4a4a6a;
}
</style>