<script setup lang="ts">
defineProps<{
  id: string
  title: string
  ownerLabel?: string | null
  coverImages?: string[]
  to?: string
}>()
</script>

<template>
  <div class="binder-card">
    <component :is="to ? 'router-link' : 'div'" :to="to" class="binder-card__link">
      <span class="binder-card__spine" aria-hidden="true">
        <span v-for="n in 3" :key="n" class="binder-card__rivet"></span>
      </span>
      <div class="binder-card__body">
        <div class="binder-card__collage" :class="`binder-card__collage--${(coverImages?.length ?? 0)}`">
          <img
            v-for="(src, i) in (coverImages ?? []).slice(0, 3)"
            :key="i"
            :src="src"
            alt=""
            class="binder-card__cover"
          />
          <div v-if="!coverImages || coverImages.length === 0" class="binder-card__empty-sleeve">
            Empty pocket
          </div>
        </div>
        <div class="binder-card__meta">
          <h3 class="binder-card__title">{{ title }}</h3>
          <span class="binder-card__owner">{{ ownerLabel ?? 'Unknown collector' }}</span>
        </div>
      </div>
    </component>
    <div v-if="$slots.actions" class="binder-card__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.binder-card { position: relative; }

.binder-card__link {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  padding-left: 22px;
  box-shadow: var(--shadow-card);
  transition: border-color 0.15s ease, transform 0.15s ease;
}
a.binder-card__link:hover { border-color: var(--color-border-strong); transform: translateY(-2px); }
.binder-card__link::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--foil-gradient);
}

.binder-card__spine {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 22px;
  background: var(--color-bg-elevated);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-5);
}
.binder-card__rivet {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--color-bg);
  box-shadow: inset 0 1px 1px rgba(0,0,0,0.6), 0 1px 0 rgba(255,255,255,0.04);
}

.binder-card__body { padding: var(--space-5); display: flex; flex-direction: column; gap: var(--space-4); }

.binder-card__collage { position: relative; height: 96px; }
.binder-card__cover {
  position: absolute;
  width: 64px; height: 88px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-strong);
  box-shadow: 0 6px 16px -6px rgba(0,0,0,0.7);
  top: 4px;
}
.binder-card__collage--1 .binder-card__cover:nth-child(1) { left: 0; transform: rotate(-2deg); }
.binder-card__collage--2 .binder-card__cover:nth-child(1) { left: 0; transform: rotate(-6deg); }
.binder-card__collage--2 .binder-card__cover:nth-child(2) { left: 56px; transform: rotate(4deg); }
.binder-card__collage--3 .binder-card__cover:nth-child(1) { left: 0; transform: rotate(-8deg); z-index: 1; }
.binder-card__collage--3 .binder-card__cover:nth-child(2) { left: 48px; transform: rotate(2deg); z-index: 2; }
.binder-card__collage--3 .binder-card__cover:nth-child(3) { left: 96px; transform: rotate(9deg); z-index: 1; }

.binder-card__empty-sleeve {
  width: 64px; height: 88px;
  border: 1.5px dashed var(--color-border-strong);
  border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  text-align: center;
  font-size: 0.65rem;
  color: var(--color-text-faint);
  padding: var(--space-2);
}

.binder-card__title { font-size: 1.05rem; color: var(--color-text); }
.binder-card__owner { font-family: var(--font-mono); font-size: 0.72rem; letter-spacing: 0.04em; color: var(--color-text-faint); }

.binder-card__actions { position: absolute; top: var(--space-3); right: var(--space-3); z-index: 5; }
</style>