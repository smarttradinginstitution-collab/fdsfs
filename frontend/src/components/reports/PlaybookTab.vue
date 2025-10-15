<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useTradesStore } from '@/stores/trades';
import { usePlaybookStore } from '@/stores/playbookStore';
import BaseButton from '@/components/ui/BaseButton.vue';
import { EllipsisVerticalIcon } from '@heroicons/vue/24/solid';
import PlaybookSelectionForm from './PlaybookSelectionForm.vue';

const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
});

const router = useRouter();
const tradesStore = useTradesStore();
const playbookStore = usePlaybookStore();

const isAddingPlaybook = ref(false);
const isDropdownOpen = ref(false);
const localCheckedRules = ref([]);

const playbook = computed(() => props.trade.playbook);
const ruleGroups = computed(() => playbookStore.ruleGroups);
const isLoading = computed(() => playbookStore.isRuleGroupsLoading);

const totalRules = computed(() => {
  return ruleGroups.value.reduce((acc, group) => acc + group.rules.length, 0);
});

const checkedCount = computed(() => {
  return localCheckedRules.value.length;
});

const progress = computed(() => {
  if (totalRules.value === 0) return 0;
  return (checkedCount.value / totalRules.value) * 100;
});

const initializeCheckedRules = () => {
  const checkedIds = props.trade.rules_followed?.map(rule => rule.id) || [];
  localCheckedRules.value = checkedIds;
};

const handleAddPlaybook = () => {
  isAddingPlaybook.value = true;
};

const handleAssignPlaybook = async (playbookId) => {
  await tradesStore.updateTrade(props.trade.id, { playbook_id: playbookId });
  isAddingPlaybook.value = false;
};

const handleCancelAdd = () => {
  isAddingPlaybook.value = false;
};

const handleSaveChanges = async () => {
    try {
        await tradesStore.updateTradeRules(props.trade.id, localCheckedRules.value);
    } catch (error) {
        console.error('Failed to save changes:', error);
    }
};

const handleEdit = () => {
  if (playbook.value) {
    router.push({ name: 'playbook-detail', params: { id: playbook.value.id } });
  }
};

const handleRemove = async () => {
  await tradesStore.updateTrade(props.trade.id, { playbook_id: null });
  isDropdownOpen.value = false;
};

watch(() => props.trade.playbook, (newPlaybook) => {
  if (newPlaybook) {
    playbookStore.fetchRuleGroups(newPlaybook.id);
  }
}, { immediate: true });

watch(() => props.trade.rules_followed, () => {
    initializeCheckedRules();
}, { deep: true, immediate: true });

onMounted(() => {
  if (playbook.value) {
    playbookStore.fetchRuleGroups(playbook.value.id);
  }
  initializeCheckedRules();
});
</script>

<template>
  <div class="playbook-tab">
    <div v-if="isAddingPlaybook">
      <PlaybookSelectionForm @assign="handleAssignPlaybook" @cancel="handleCancelAdd" />
    </div>
    <div v-else-if="!playbook" class="no-playbook">
      <p>No playbook assigned to this trade.</p>
      <BaseButton @click="handleAddPlaybook">Add Playbook</BaseButton>
    </div>
    <div v-else class="playbook-details">
      <div class="playbook-header">
        <h3>{{ playbook.title }}</h3>
        <div class="actions">
          <BaseButton @click="handleSaveChanges" size="small" class="save-button">Save Changes</BaseButton>
          <div class="dropdown-container">
            <button @click="isDropdownOpen = !isDropdownOpen" class="icon-button">
              <EllipsisVerticalIcon class="icon" />
            </button>
            <div v-if="isDropdownOpen" class="dropdown-menu">
              <a @click="handleEdit" class="dropdown-item">Edit</a>
              <a @click="handleRemove" class="dropdown-item">Remove</a>
            </div>
          </div>
        </div>
      </div>
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: progress + '%' }"></div>
      </div>
      <div class="rules-followed-text">
        Rules Followed: {{ checkedCount }} / {{ totalRules }}
      </div>
      <div v-if="isLoading" class="loading">Loading rules...</div>
      <div v-else class="rule-groups-container">
        <div v-for="group in ruleGroups" :key="group.id" class="rule-group-card">
          <h4 class="rule-group-title">{{ group.name_group }}</h4>
          <ul class="rules-list">
            <li v-for="rule in group.rules" :key="rule.id" :class="{ 'rule-checked': localCheckedRules.includes(rule.id) }">
              <label class="rule-label">
                <input
                  type="checkbox"
                  class="custom-checkbox-input"
                  :value="rule.id"
                  v-model="localCheckedRules"
                />
                <span class="custom-checkbox-visual"></span>
                <span class="rule-text">{{ rule.rule }}</span>
              </label>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.save-button {
  background-color: rgba(76, 175, 80, 0.6);
  color: white;
  border-color: transparent;
}

.save-button:hover:not(:disabled) {
  background-color: rgba(76, 175, 80, 0.8);
}

.save-button:disabled {
  background-color: rgba(76, 175, 80, 0.3);
  cursor: not-allowed;
}

.playbook-tab {
  padding: 1rem;
}
.no-playbook {
  text-align: center;
  padding: 2rem;
}
.playbook-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.dropdown-container {
  position: relative;
}
.icon-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
}
.icon {
  width: 1.5rem;
  height: 1.5rem;
  color: var(--semantic-color-text-secondary);
}
.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  background-color: var(--semantic-color-surface-secondary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  z-index: 10;
  width: 120px;
  padding: var(--semantic-size-inset-sm);
}
.dropdown-item {
  display: block;
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  cursor: pointer;
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-primary);
  border-radius: var(--semantic-border-radius-interactive);
}
.dropdown-item:hover {
  background-color: var(--semantic-color-surface-secondary);
}
.progress-bar-container {
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}
.progress-bar {
  height: 7px;
  background-color: var(--semantic-color-interactive-primary-default);
  border-radius: 4px;
  transition: width 0.3s ease-in-out;
}
.rules-followed-text {
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}
.rule-groups-container {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-inset-md);
  margin-top: 1rem;
}
.rule-group-card {
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--semantic-size-inset-lg);
}
.rule-group-title {
  font: var(--semantic-font-style-heading-sm);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-md);
}
.rules-list {
  list-style-type: none;
  padding-left: 0;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-gap-md);
}
.rule-label {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-primary);
}
.custom-checkbox-input {
  display: none; /* Nascondi la checkbox di default */
}

.custom-checkbox-visual {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-container);
  position: relative;
  transition: background-color 0.2s, border-color 0.2s;
}

.custom-checkbox-input:checked + .custom-checkbox-visual {
  background-color: var(--semantic-color-interactive-primary-default);
  border-color: var(--semantic-color-interactive-primary-default);
}

.custom-checkbox-input:checked + .custom-checkbox-visual::after {
  content: '';
  position: absolute;
  left: 3px;
  width: 4px;
  height: 8px;
  border: solid var(--semantic-color-text-on-brand);
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.rule-checked .rule-text {
  text-decoration: line-through;
  opacity: 0.6;
}

.rule-label {
  transition: opacity 0.3s ease;
}
</style>