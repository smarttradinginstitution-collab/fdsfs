<template>
  <TradePlaybookWidget :trade="trade" />
</template>

<script setup>
import TradePlaybookWidget from '@/components/Playbooks/TradePlaybookWidget.vue';

defineProps({
  trade: {
    type: Object,
    required: true,
  },
});
</script>