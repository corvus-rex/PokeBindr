<template>
  <div class="binder-skeleton" aria-hidden="true">
    <div class="binder-skeleton__spine"></div>
    <div class="binder-skeleton__body">
      <div class="binder-skeleton__collage">
        <span class="shimmer"></span>
        <span class="shimmer"></span>
        <span class="shimmer"></span>
      </div>
      <div class="shimmer binder-skeleton__line binder-skeleton__line--title"></div>
      <div class="shimmer binder-skeleton__line binder-skeleton__line--owner"></div>
    </div>
  </div>
</template>

<style scoped>
.binder-skeleton {
  position: relative;
  display: flex;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding-left: 22px;
  overflow: hidden;
}
.binder-skeleton__spine { position: absolute; left: 0; top: 0; bottom: 0; width: 22px; background: var(--color-bg-elevated); border-right: 1px solid var(--color-border); }
.binder-skeleton__body { padding: var(--space-5); display: flex; flex-direction: column; gap: var(--space-4); width: 100%; }
.binder-skeleton__collage { display: flex; gap: var(--space-2); height: 88px; }
.binder-skeleton__collage .shimmer { width: 64px; height: 88px; border-radius: var(--radius-sm); }
.binder-skeleton__line { height: 14px; border-radius: 4px; }
.binder-skeleton__line--title { width: 60%; }
.binder-skeleton__line--owner { width: 35%; height: 10px; }

.shimmer {
  background: linear-gradient(100deg, var(--color-surface-raised) 30%, var(--color-border) 50%, var(--color-surface-raised) 70%);
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>