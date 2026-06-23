<script setup lang="ts">
defineEmits<{ retry: [] }>()
defineProps<{ message?: string }>()
</script>

<template>
  <div class="error-state alert alert-danger">
    <p>{{ message ?? 'Something went wrong while loading this. Try again.' }}</p>
    <button class="btn btn-ghost" @click="$emit('retry')">Retry</button>
  </div>
</template>

<style scoped>
.error-state { display: flex; align-items: center; justify-content: space-between; gap: var(--space-4); flex-wrap: wrap; }
</style>