<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { onClickOutside } from '@vueuse/core';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import BuildingLibraryIcon from '../icons/BuildingLibraryIcon.vue';
import ChevronDownIcon from '../icons/ChevronDownIcon.vue';
import BaseCheckbox from './BaseCheckbox.vue';
import BaseButton from './BaseButton.vue';

// Stores and Router
const tradingAccountsStore = useTradingAccountsStore();
const router = useRouter();

// Component State
const isDropdownOpen = ref(false);
const selectorRef = ref(null);
const localSelectionIds = ref([]);

// Computed Properties
const selectedAccounts = computed(() => tradingAccountsStore.selectedTradingAccounts);
const accounts = computed(() => tradingAccountsStore.tradingAccounts);
const isDisabled = computed(() => accounts.value.length === 0);

// Display text for the selector
const mainText = computed(() => {
  if (selectedAccounts.value.length === 0) return 'Nessun account';
  if (selectedAccounts.value.length === 1) return selectedAccounts.value[0].label;
  return `${selectedAccounts.value.length} account selezionati`;
});

const subText = computed(() => {
  if (selectedAccounts.value.length === 0) return 'Selezionane uno';
  if (selectedAccounts.value.length === 1) return selectedAccounts.value[0].broker?.name || 'N/D';
  return 'Visualizzazione aggregata';
});

// Methods
function toggleDropdown() {
  if (isDisabled.value) return;
  isDropdownOpen.value = !isDropdownOpen.value;
  // Quando apriamo il dropdown, sincronizziamo la selezione locale con lo store
  if (isDropdownOpen.value) {
    localSelectionIds.value = [...tradingAccountsStore.selectedTradingAccountIds];
  }
}

async function applySelection() {
  await tradingAccountsStore.updateAccountSelection(localSelectionIds.value);
  isDropdownOpen.value = false;
}

// Close dropdown when clicking outside and apply changes
onClickOutside(selectorRef, () => {
  if (isDropdownOpen.value) {
    applySelection();
  }
});

// Fetch accounts on mount
onMounted(() => {
  if (tradingAccountsStore.tradingAccounts.length === 0) {
    tradingAccountsStore.fetchTradingAccounts();
  }
});

// Watch for changes in the store's selection to update the local state
watch(
  () => tradingAccountsStore.selectedTradingAccountIds,
  (newIds) => {
    localSelectionIds.value = [...newIds];
  },
  { deep: true }
);
</script>

<template>
  <div
    ref="selectorRef"
    class="account-selector"
    :class="{ 'is-disabled': isDisabled, 'is-open': isDropdownOpen }"
    @click="toggleDropdown"
  >
    <BuildingLibraryIcon class="icon bank-icon" />
    <div class="text-container">
      <span class="account-name">{{ mainText }}</span>
      <span class="broker-name">{{ subText }}</span>
    </div>
    <ChevronDownIcon v-if="!isDisabled" class="icon chevron-icon" />

    <transition name="fade">
      <div v-if="isDropdownOpen && !isDisabled" class="dropdown-menu">
        <div class="dropdown-content">
          <label
            v-for="account in accounts"
            :key="account.id"
            class="dropdown-item"
            :for="`dd-account-${account.id}`"
          >
            <BaseCheckbox
              :id="`dd-account-${account.id}`"
              :value="account.id"
              v-model="localSelectionIds"
            >
              <span class="account-name-dd">{{ account.label }}</span>
            </BaseCheckbox>
          </label>
        </div>
        <div class="dropdown-footer">
          <BaseButton @click.stop="applySelection" size="small" variant="primary" class="apply-button">
            Applica
          </BaseButton>
        </div>
      </div>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.account-selector {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s, border-color 0.2s;

  // Stili replicati da DropdownButton.vue per coerenza visiva
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--base-size-spacing-2) var(--base-size-spacing-3); /* 8px vertical, 12px horizontal */
  color: var(--semantic-color-text-secondary);

  &:not(.is-disabled):hover {
    background-color: var(--semantic-color-surface-secondary);
  }

  &.is-open {
    border-color: var(--semantic-color-border-focus);
    box-shadow: var(--semantic-effect-shadow-focus-ring);
  }
}

.is-disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.icon {
  flex-shrink: 0;
  color: var(--semantic-color-text-secondary);
}

.bank-icon {
  width: 20px;
  height: 20px;
}

.text-container {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  text-align: left;
}

.account-name {
  font: var(--semantic-font-style-label-md);
  font-size: 9px; // Dimensione custom
  font-weight: 500;
  color: var(--semantic-color-text-primary);
}

.broker-name {
  font-size: 9px; // Dimensione custom
  color: var(--semantic-color-text-secondary);
}

.chevron-icon {
  width: 16px;
  height: 16px;
  margin-left: auto;
  transition: transform 0.2s;
}

.is-open .chevron-icon {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  min-width: 220px;
  background-color: var(--semantic-color-bg-default);
  border: 1px solid var(--semantic-color-border-muted);
  border-radius: var(--semantic-border-radius-interactive);
  box-shadow: var(--semantic-shadow-md);
  z-index: 1000;
  overflow: hidden;
}

.dropdown-content {
  max-height: 250px;
  overflow-y: auto;
  padding: 4px;
}

.dropdown-item {
  display: block;
  padding: 8px 12px;
  cursor: pointer;
  list-style: none;
  transition: background-color 0.2s;
  border-radius: var(--semantic-border-radius-interactive);

  &:hover {
    background-color: var(--semantic-color-bg-subtle);
  }
}

.account-name-dd {
  font-size: 14px;
  color: var(--semantic-color-text-primary);
}

.dropdown-footer {
  padding: 8px;
  border-top: 1px solid var(--semantic-color-border-muted);
  background-color: var(--semantic-color-surface-primary);
}

.apply-button {
  width: 100%;
}

/* Fade Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>