<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { onClickOutside } from '@vueuse/core';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import BuildingLibraryIcon from '../icons/BuildingLibraryIcon.vue';
import ChevronDownIcon from '../icons/ChevronDownIcon.vue';

// Stores and Router
const tradingAccountsStore = useTradingAccountsStore();
const router = useRouter();

// Component State
const isDropdownOpen = ref(false);
const selectorRef = ref(null);

// Computed Properties
const selectedAccount = computed(() => tradingAccountsStore.selectedTradingAccount);
const accounts = computed(() => tradingAccountsStore.tradingAccounts);
const isDisabled = computed(() => accounts.value.length <= 1);
const hasNoAccounts = computed(() => accounts.value.length === 0);

// Methods
function toggleDropdown() {
  if (isDisabled.value) {
    if (hasNoAccounts.value) {
      router.push({ path: '/add-account' });
    }
    return;
  }
  isDropdownOpen.value = !isDropdownOpen.value;
}

function selectAccount(account) {
  tradingAccountsStore.selectTradingAccount(account);
  isDropdownOpen.value = false;
}

// Close dropdown when clicking outside
onClickOutside(selectorRef, () => {
  isDropdownOpen.value = false;
});

// Fetch accounts on mount
onMounted(() => {
  if (!tradingAccountsStore.hasTradingAccounts) {
    tradingAccountsStore.fetchTradingAccounts();
  }
});
</script>

<template>
  <div
    ref="selectorRef"
    class="account-selector"
    :class="{ 'is-disabled': isDisabled, 'is-open': isDropdownOpen }"
    @click="toggleDropdown"
  >
    <BuildingLibraryIcon class="icon bank-icon" />
    <div v-if="selectedAccount" class="text-container">
      <span class="account-name">{{ selectedAccount.label }}</span>
      <span class="broker-name">{{ selectedAccount.broker_name }}</span>
    </div>
    <div v-else-if="hasNoAccounts" class="text-container">
      <span class="account-name">Nessun account</span>
      <span class="broker-name">Aggiungine uno</span>
    </div>
    <div v-else class="text-container">
      <span class="account-name">Seleziona</span>
      <span class="broker-name">un account</span>
    </div>
    <ChevronDownIcon v-if="!isDisabled" class="icon chevron-icon" />

    <transition name="fade">
      <div v-if="isDropdownOpen && !isDisabled" class="dropdown-menu">
        <ul>
          <li
            v-for="account in accounts"
            :key="account.id"
            @click.stop="selectAccount(account)"
            class="dropdown-item"
          >
            <div class="text-container">
              <span class="account-name">{{ account.label }}</span>
              <span class="broker-name">{{ account.broker_name }}</span>
            </div>
          </li>
        </ul>
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
  font-size: 13px; // Dimensione custom come da richiesta originale
  font-weight: 500;
  color: var(--semantic-color-text-primary);
}

.broker-name {
  font-size: 11px; // Dimensione custom
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

.dropdown-item {
  padding: 8px 12px;
  cursor: pointer;
  list-style: none;
  transition: background-color 0.2s;
  border-radius: var(--semantic-border-radius-interactive);

  &:hover {
    background-color: var(--semantic-color-bg-subtle);
  }
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