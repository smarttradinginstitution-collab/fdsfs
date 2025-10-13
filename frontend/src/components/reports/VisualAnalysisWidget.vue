<script setup>
import { computed } from 'vue';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import TradeImageGallery from '@/components/images/TradeImageGallery.vue';

const props = defineProps({
  tradeId: {
    type: String,
    required: true,
  },
  images: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(['edit-image', 'open-lightbox']);

const primaryBeforeImage = computed(() => props.images.find(img => img.is_primary_before));
const primaryAfterImage = computed(() => props.images.find(img => img.is_primary_after));

const handleEditImage = (image) => {
  emit('edit-image', image);
};

const handleOpenLightbox = (index) => {
  emit('open-lightbox', index);
};
</script>

<template>
  <BaseWidget v-if="primaryBeforeImage || primaryAfterImage || images.length > 0" class="visual-analysis-widget">
    <h3 class="widget-title">Visual Analysis</h3>

    <div v-if="primaryBeforeImage || primaryAfterImage" class="chart-comparison">
      <div class="chart-container">
        <h4>Before</h4>
        <img v-if="primaryBeforeImage" :src="primaryBeforeImage.url" alt="Before chart" />
        <div v-else class="placeholder">Not set</div>
      </div>
      <div class="chart-container">
        <h4>After</h4>
        <img v-if="primaryAfterImage" :src="primaryAfterImage.url" alt="After chart" />
        <div v-else class="placeholder">Not set</div>
      </div>
    </div>

    <hr v-if="primaryBeforeImage || primaryAfterImage" class="section-divider" />

    <TradeImageGallery
      :trade-id="tradeId"
      :images="images"
      mode="gallery-only"
      @edit-image="handleEditImage"
      @open-lightbox="handleOpenLightbox"
    />
  </BaseWidget>
</template>

<style lang="scss" scoped>
.visual-analysis-widget {
  padding: var(--semantic-size-inset-lg);
  .widget-title {
    font: var(--semantic-font-style-heading-md);
    margin-bottom: var(--semantic-size-stack-md);
  }
}

.chart-comparison {
  display: flex;
  gap: var(--semantic-size-gap-lg);
}

.chart-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);

  h4 {
    font: var(--semantic-font-style-label-lg);
    color: var(--semantic-color-text-secondary);
  }

  img {
    width: 100%;
    height: auto;
    border-radius: var(--semantic-border-radius-container);
    border: 1px solid var(--semantic-color-border-default);
  }

  .placeholder {
    width: 100%;
    aspect-ratio: 16 / 9;
    border-radius: var(--semantic-border-radius-container);
    background-color: var(--semantic-color-surface-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--semantic-color-text-secondary);
    font-style: italic;
  }
}

.section-divider {
  border: none;
  border-top: 1px solid var(--semantic-color-border-default);
  margin: var(--semantic-size-gap-lg) 0;
}
</style>