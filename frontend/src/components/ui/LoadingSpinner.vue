<template>
  <div class="spinner">
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
  </div>
</template>

<style scoped>
.spinner {
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.bar {
  width: 6px;
  height: 100%;
  background-color: var(--semantic-color-action-primary-default);
  animation: equalizer 1.2s infinite ease-in-out;
  transform-origin: bottom;
}

/* Apply different animation delays to each bar for the equalizer effect */
.bar:nth-child(1) {
  animation-delay: 0s;
}
.bar:nth-child(2) {
  animation-delay: -1.1s;
}
.bar:nth-child(3) {
  animation-delay: -1.0s;
}
.bar:nth-child(4) {
  animation-delay: -0.9s;
}
.bar:nth-child(5) {
  animation-delay: -0.8s;
}

@keyframes equalizer {
  0%, 100% {
    transform: scaleY(0.1);
  }
  50% {
    transform: scaleY(1.0);
  }
}
</style>