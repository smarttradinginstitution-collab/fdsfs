<template>
  <div class="report-detail-skeleton">
    <!-- Header Skeleton -->
    <header class="report-header-skeleton">
      <div class="navigation-controls-skeleton">
        <BaseSkeleton width="40px" height="36px" border-radius="var(--semantic-border-radius-interactive)" />
        <BaseSkeleton width="40px" height="36px" border-radius="var(--semantic-border-radius-interactive)" />
      </div>
      <div class="trade-identifier-skeleton">
        <BaseSkeleton width="200px" height="2.5rem" border-radius="var(--semantic-border-radius-pill)" />
        <BaseSkeleton width="150px" height="1rem" border-radius="var(--semantic-border-radius-pill)" style="margin-top: 8px;" />
      </div>
      <div class="action-buttons-skeleton">
        <BaseSkeleton width="120px" height="36px" border-radius="var(--semantic-border-radius-interactive)" />
        <BaseSkeleton width="80px" height="36px" border-radius="var(--semantic-border-radius-interactive)" />
        <BaseSkeleton width="80px" height="36px" border-radius="var(--semantic-border-radius-interactive)" />
      </div>
    </header>

    <!-- Content Skeleton -->
    <main class="report-content-skeleton">
      <!-- Left Column Skeleton -->
      <div class="left-column-skeleton">
        <BaseSkeleton height="400px" />
      </div>

      <!-- Right Column Skeleton -->
      <div class="right-column-skeleton">
        <BaseSkeleton height="300px" />
        <BaseSkeleton height="350px" />
      </div>
    </main>
  </div>
</template>

<script setup>
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue';
</script>

<style lang="scss" scoped>
// Ricalca la struttura e gli stili di ReportView.vue per coerenza
.report-detail-skeleton {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--semantic-size-inset-lg);
  gap: var(--semantic-size-gap-lg);
}

.report-header-skeleton {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--semantic-size-inset-lg);
}

.navigation-controls-skeleton,
.action-buttons-skeleton {
  display: flex;
  gap: var(--semantic-size-stack-sm);
}

.trade-identifier-skeleton {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.report-content-skeleton {
  display: flex;
  flex-grow: 1;
  gap: var(--semantic-size-stack-lg);
  min-height: 0;
}

.left-column-skeleton,
.right-column-skeleton {
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: var(--semantic-size-stack-lg);
}

.left-column-skeleton {
  flex: 0 0 33%;
}

.right-column-skeleton {
  flex: 1;
}
</style>
