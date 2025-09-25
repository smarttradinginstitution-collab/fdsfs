<template>
  <div class="trading-account-selector" v-if="hasTradingAccounts">
    <div class="relative">
      <button @click="toggleDropdown" class="flex items-center p-2 bg-gray-700 rounded-md">
        <span class="mr-2">{{ selectedTradingAccount?.label || 'Select Account' }}</span>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
      </button>
      <div v-if="isDropdownOpen" class="absolute right-0 mt-2 w-48 bg-gray-800 rounded-md shadow-lg z-10">
        <ul>
          <li
            v-for="account in tradingAccounts"
            :key="account.id"
            @click="selectAccount(account)"
            class="px-4 py-2 hover:bg-gray-700 cursor-pointer"
          >
            {{ account.label }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import { storeToRefs } from 'pinia';

const tradingAccountsStore = useTradingAccountsStore();
const { tradingAccounts, selectedTradingAccount, hasTradingAccounts } = storeToRefs(tradingAccountsStore);
const { selectTradingAccount } = tradingAccountsStore;

const isDropdownOpen = ref(false);

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
};

const selectAccount = (account) => {
  selectTradingAccount(account);
  isDropdownOpen.value = false;
};
</script>

<style scoped>
/* Using utility classes, but you can add specific styles here if needed */
.relative {
  position: relative;
}
.absolute {
  position: absolute;
}
/* Add other styles as needed */
</style>