<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useTradesStore } from '@/stores/trades';
import { usePlaybookStore } from '@/stores/playbookStore';
import BaseButton from '@/components/ui/BaseButton.vue';
import SelectPlaybookModal from './SelectPlaybookModal.vue';

const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
});

const tradesStore = useTradesStore();
const playbookStore = usePlaybookStore();

const isModalOpen = ref(false);
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
  isModalOpen.value = true;
};

const handleSelectPlaybook = async (playbookId) => {
  await tradesStore.updateTrade(props.trade.id, { playbook_id: playbookId });
  isModalOpen.value = false;
};

const handleSaveChanges = async () => {
    try {
        await tradesStore.updateTradeRules(props.trade.id, localCheckedRules.value);
    } catch (error) {
        console.error('Failed to save changes:', error);
    }
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
    <div v-if="!playbook" class="no-playbook">
      <p>No playbook assigned to this trade.</p>
      <BaseButton @click="handleAddPlaybook">Add Playbook</BaseButton>
    </div>
    <div v-else class="playbook-details">
      <div class="playbook-header">
        <h3>{{ playbook.title }}</h3>
        <BaseButton @click="handleSaveChanges">Save Changes</BaseButton>
      </div>
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: progress + '%' }"></div>
      </div>
      <div class="rules-followed-text">
        Rules Followed: {{ checkedCount }} / {{ totalRules }}
      </div>
      <div v-if="isLoading" class="loading">Loading rules...</div>
      <div v-else class="rule-groups-container">
        <div v-for="group in ruleGroups" :key="group.id" class="rule-group">
          <h4>{{ group.name_group }}</h4>
          <ul>
            <li v-for="rule in group.rules" :key="rule.id">
              <label>
                <input
                  type="checkbox"
                  :value="rule.id"
                  v-model="localCheckedRules"
                />
                {{ rule.rule }}
              </label>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <SelectPlaybookModal
      :show="isModalOpen"
      @close="isModalOpen = false"
      @select="handleSelectPlaybook"
    />
  </div>
</template>

<style scoped>
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
.progress-bar-container {
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}
.progress-bar {
  height: 10px;
  background-color: #4caf50;
  border-radius: 4px;
}
.rules-followed-text {
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}
.rule-groups-container {
  margin-top: 1rem;
}
.rule-group {
  margin-bottom: 1.5rem;
}
.rule-group h4 {
  font-weight: bold;
  margin-bottom: 0.5rem;
}
ul {
  list-style-type: none;
  padding-left: 0;
}
li {
  margin-bottom: 0.5rem;
}
label {
  display: flex;
  align-items: center;
}
input[type="checkbox"] {
  margin-right: 0.5rem;
}
</style>