<script setup>
import { ref, watch, computed } from 'vue';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseInput from '@/components/ui/BaseInput.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import InfoIcon from '@/components/icons/InfoIcon.vue';

const props = defineProps({
  modelValue: { type: Boolean, required: true }, // For v-model on the modal visibility
  trade: { type: Object, required: true },
});

const emit = defineEmits(['update:modelValue', 'save']);

const form = ref({});

// When the modal opens, populate the form with the trade's current data
watch(() => props.trade, (newTrade) => {
  if (newTrade) {
    form.value = {
      gross_p_l: newTrade.gross_p_l ?? '',
      take_profit_price: newTrade.take_profit_price ?? '',
      stop_loss_price: newTrade.stop_loss_price ?? '',
      highest_price_during_trade: newTrade.highest_price_during_trade ?? '',
      lowest_price_during_trade: newTrade.lowest_price_during_trade ?? '',
      commissions: newTrade.commissions ?? '',
    };
  }
}, { immediate: true });

const netPnl = computed(() => {
  const grossPnl = parseFloat(form.value.gross_p_l) || 0;
  const commissions = parseFloat(form.value.commissions) || 0;
  const fees = parseFloat(props.trade.fees) || 0; // Fees are not editable in this modal
  return (grossPnl - commissions - fees).toFixed(2);
});

const highLowTooltipText = computed(() => {
    if(!props.trade.direction) return "Set the trade direction first.";
    if(props.trade.direction === 'LONG') {
        return "For LONG trades, Highest Price is your MFE (Max Favorable Excursion) and Lowest Price is your MAE (Max Adverse Excursion).";
    } else { // SHORT
        return "For SHORT trades, Lowest Price is your MFE (Max Favorable Excursion) and Highest Price is your MAE (Max Adverse Excursion).";
    }
});

const handleSave = () => {
  // Convert empty strings to null and string numbers to actual numbers
  const payload = {};
  for (const key in form.value) {
    const value = form.value[key];
    payload[key] = value === '' ? null : Number(value);
  }
  emit('save', payload);
  closeModal();
};

const closeModal = () => {
  emit('update:modelValue', false);
};
</script>

<template>
  <BaseModal :show="modelValue" @close="closeModal" title="Edit Trade Details">
    <form @submit.prevent="handleSave" class="edit-trade-form">
      <div class="form-grid">
        <BaseInput
          v-model="form.take_profit_price"
          label="Take Profit Price"
          type="number"
          step="any"
          placeholder="Enter price"
        />
        <BaseInput
          v-model="form.stop_loss_price"
          label="Stop Loss Price"
          type="number"
          step="any"
          placeholder="Enter price"
        />
        <div class="input-with-info">
          <BaseInput
            v-model="form.highest_price_during_trade"
            label="Highest Price During Trade"
            type="number"
            step="any"
            placeholder="Enter price"
          />
          <div class="info-icon-wrapper" :title="highLowTooltipText">
            <InfoIcon class="info-icon" />
          </div>
        </div>
        <div class="input-with-info">
          <BaseInput
            v-model="form.lowest_price_during_trade"
            label="Lowest Price During Trade"
            type="number"
            step="any"
            placeholder="Enter price"
          />
          <div class="info-icon-wrapper" :title="highLowTooltipText">
            <InfoIcon class="info-icon" />
          </div>
        </div>
      </div>

      <div class="pnl-section">
        <BaseInput
            v-model="form.gross_p_l"
            label="Gross P&L"
            type="number"
            step="any"
        />
        <BaseInput
            v-model="form.commissions"
            label="Commissions"
            type="number"
            step="any"
        />
        <div class="net-pnl-display">
            <label class="net-pnl-label">Net P&L (Calculated)</label>
            <span class="net-pnl-value">{{ netPnl }}</span>
        </div>
      </div>

      <div class="form-actions">
        <BaseButton @click="closeModal" type="button" variant="secondary">Cancel</BaseButton>
        <BaseButton type="submit" variant="primary">Save Changes</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<style lang="scss" scoped>
.edit-trade-form {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--semantic-size-stack-md);
}

.pnl-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--semantic-size-stack-md);
  align-items: flex-end; /* Align items to the bottom */
  border-top: 1px solid var(--semantic-color-border-default);
  padding-top: var(--semantic-size-stack-lg);
}

.net-pnl-display {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  padding-bottom: 8px; /* Adjust to align with input fields */
}

.net-pnl-label {
  font-size: var(--font-size-sm);
  color: var(--semantic-color-text-secondary);
}

.net-pnl-value {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--semantic-color-text-primary);
}

.input-with-info {
  position: relative;

  .info-icon-wrapper {
    position: absolute;
    top: 0;
    right: 0;
    cursor: help;
  }

  .info-icon {
    width: 16px;
    height: 16px;
    color: var(--semantic-color-text-tertiary);
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
}
</style>