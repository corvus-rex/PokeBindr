<script setup lang="ts">
defineProps<{ title: string; message?: string }>()
</script>

<template>
  <div class="empty-state panel">
    <div class="empty-state__icon" aria-hidden="true">
      <span></span><span></span>
    </div>
    <h3 class="empty-state__title">{{ title }}</h3>
    <p v-if="message" class="empty-state__message">{{ message }}</p>
    <div class="empty-state__action"><slot /></div>
  </div>
</template>

<style scoped>
.empty-state { display: flex; flex-direction: column; align-items: center; text-align: center; gap: var(--space-3); padding: var(--space-7) var(--space-5); }
.empty-state__icon { width: 56px; height: 44px; position: relative; margin-bottom: var(--space-2); }
.empty-state__icon span { position: absolute; width: 30px; height: 40px; border: 1.5px dashed var(--color-border-strong); border-radius: var(--radius-sm); }
.empty-state__icon span:first-child { left: 0; transform: rotate(-6deg); }
.empty-state__icon span:last-child { left: 20px; transform: rotate(6deg); }
.empty-state__title { color: var(--color-text); font-size: 1.05rem; }
.empty-state__message { color: var(--color-text-muted); font-size: 0.9rem; max-width: 360px; }
</style>