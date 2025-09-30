<script setup>
import { ref, onMounted, watch } from 'vue';
import apiClient from '@/services/api';
import { useUiStore } from '@/stores/uiStore';
import BaseCard from '@/components/ui/BaseCard.vue';
import BaseButton from '@/components/ui/BaseButton.vue';

const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
});

const uiStore = useUiStore();
const allRules = ref([]);
const selectedRuleIds = ref(new Set());
const isLoading = ref(false);

// Fetch all rules for the playbook associated with the trade
const fetchPlaybookRules = async (playbookId) => {
  if (!playbookId) return;
  try {
    // This assumes an endpoint exists to get rule groups (with rules) for a playbook.
    const response = await apiClient.get(`/playbooks/${playbookId}/rule-groups/`);
    // Flatten the rules from all groups into a single list
    allRules.value = response.data.flatMap(group => group.rules);
  } catch (error) {
    console.error("Failed to fetch playbook rules:", error);
    uiStore.showNotification({ message: 'Error loading playbook rules.', type: 'error' });
  }
};

// Fetch the rules that are already linked to this specific trade
const fetchSelectedTradeRules = async (tradeId) => {
    if (!tradeId) return;
    try {
        const response = await apiClient.get(`/trades/${tradeId}/rules`);
        selectedRuleIds.value = new Set(response.data.map(rule => rule.id));
    } catch (error) {
        console.error("Failed to fetch selected trade rules:", error);
    }
};

const handleSave = async () => {
    isLoading.value = true;
    try {
        await apiClient.put(`/trades/${props.trade.id}/rules`, {
            rule_ids: Array.from(selectedRuleIds.value),
        });
        uiStore.showNotification({ message: 'Rules updated successfully!', type: 'success' });
    } catch (error) {
        console.error("Failed to save trade rules:", error);
        uiStore.showNotification({ message: 'Error saving rules.', type: 'error' });
    } finally {
        isLoading.value = false;
    }
};

// Watch for the trade prop to be loaded and then fetch data
watch(() => props.trade, (newTrade) => {
  if (newTrade && newTrade.id && newTrade.playbook?.id) {
    fetchPlaybookRules(newTrade.playbook.id);
    fetchSelectedTradeRules(newTrade.id);
  }
}, { immediate: true });

</script>

<template>
  <BaseCard>
    <h2 class="card-title">Followed Rules</h2>
    <div v-if="!trade.playbook">
        <p>This trade is not associated with a playbook.</p>
    </div>
    <div v-else-if="allRules.length === 0">
        <p>This playbook has no rules defined.</p>
    </div>
    <div v-else class="rules-checklist">
      <div v-for="rule in allRules" :key="rule.id" class="checkbox-item">
        <input
          type="checkbox"
          :id="`rule-${rule.id}`"
          :value="rule.id"
          v-model="selectedRuleIds"
          @change="(e) => {
            if (e.target.checked) {
              selectedRuleIds.add(rule.id);
            } else {
              selectedRuleIds.delete(rule.id);
            }
          }"
          :checked="selectedRuleIds.has(rule.id)"
        />
        <label :for="`rule-${rule.id}`">{{ rule.rule }}</label>
      </div>
      <BaseButton @click="handleSave" :is-loading="isLoading" class="save-button">
        Save Rules
      </BaseButton>
    </div>
  </BaseCard>
</template>

<style scoped>
.card-title {
  font: var(--semantic-font-style-heading-h5);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-lg);
}
.rules-checklist {
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-md);
}
.checkbox-item {
    display: flex;
    align-items: center;
    gap: var(--semantic-size-stack-sm);
}
.save-button {
    margin-top: var(--semantic-size-stack-lg);
    align-self: flex-start;
}
</style>