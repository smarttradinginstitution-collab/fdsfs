<script setup>
import { computed } from 'vue';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import DropdownButton from './DropdownButton.vue';
import BuildingLibraryIcon from '../icons/BuildingLibraryIcon.vue';

const tradingAccountsStore = useTradingAccountsStore();

const selectedAccount = computed(() => tradingAccountsStore.selectedTradingAccount);
const allAccounts = computed(() => tradingAccountsStore.tradingAccounts);

const isDisabled = computed(() => allAccounts.value.length <= 1);

function selectAccount(account) {
  if (account.id === selectedAccount.value.id) return;
  tradingAccountsStore.selectTradingAccount(account);
}
</script>

<template>
  <div v-if="selectedAccount" class="account-selector-wrapper">
    <DropdownButton :disabled="isDisabled" class="account-selector">
      <template #icon>
        <BuildingLibraryIcon />
      </template>

      <template #text>
        <div class="trigger-text-wrapper">
          <span class="account-name">{{ selectedAccount.label }}</span>
          <span class="broker-name">{{ selectedAccount.broker?.name || 'N/A' }}</span>
        </div>
      </template>

      <template #content>
        <ul class="account-list">
          <li
            v-for="account in allAccounts"
            :key="account.id"
            class="account-item"
            :class="{ 'is-selected': account.id === selectedAccount.id }"
            @click="selectAccount(account)"
          >
            <div class="account-item-info">
              <span class="account-item-name">{{ account.label }}</span>
              <span class="account-item-broker">{{ account.broker?.name }}</span>
            </div>
            <svg
              v-if="account.id === selectedAccount.id"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              class="check-icon"
            >
              <path
                fill-rule="evenodd"
                d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.052-.143z"
                clip-rule="evenodd"
              />
            </svg>
          </li>
        </ul>
      </template>
    </DropdownButton>
  </div>
</template>

<style scoped lang="scss">
.account-selector :deep(.dropdown-trigger) {
  gap: var(--semantic-size-stack-xs);
  height: 100%;
  padding-top: var(--base-size-spacing-1);
  padding-bottom: var(--base-size-spacing-1);
}

.account-selector :deep(.trigger-icon svg) {
  width: 20px;
  height: 20px;
}

.account-selector :deep(.dropdown-trigger[disabled]) {
  cursor: not-allowed;
  opacity: 0.6;
}

.trigger-text-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.2;
}

.account-name, .account-item-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px; /* Adjust as needed */
}

.account-name {
  font: var(--semantic-font-style-label-xs);
  color: var(--semantic-color-text-primary);
}

.broker-name {
  font: var(--semantic-font-style-body-xxs);
  color: var(--semantic-color-text-secondary);
}

.account-list {
  list-style: none;
  padding: 0;
  margin: 0;
  min-width: 220px;
}

.account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--semantic-size-spacing-2) var(--semantic-size-spacing-3);
  cursor: pointer;
  border-radius: var(--semantic-border-radius-interactive);
  transition: background-color 0.2s ease-in-out;

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
  }
}

.account-item-info {
  display: flex;
  flex-direction: column;
}

.account-item-name {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);
}

.account-item-broker {
  font: var(--semantic-font-style-body-xs);
  color: var(--semantic-color-text-secondary);
}

.check-icon {
  width: 16px;
  height: 16px;
  color: var(--semantic-color-feedback-positive-text);
}
</style>