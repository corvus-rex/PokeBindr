<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { authStore } from '../stores/auth'
import { binderService, type BinderPublicSummary } from '../services/binderService'
import BinderCard from '../components/BinderCard.vue'
import BinderCardSkeleton from '../components/BinderCardSkeleton.vue'
import EmptyState from '../components/EmptyState.vue'
import ErrorState from '../components/ErrorState.vue'

const isAuthenticated = authStore.isAuthenticated()
const recentBinders = ref<BinderPublicSummary[]>([])
const status = ref<'loading' | 'ready' | 'empty' | 'error'>('loading')

function ownerLabel(ownerId: string): string {
  return `Collector #${ownerId.slice(-6).toUpperCase()}`
}

async function loadRecent() {
  status.value = 'loading'
  try {
    const result = await binderService.listRecentPublic(8)
    recentBinders.value = result
    status.value = result.length === 0 ? 'empty' : 'ready'
  } catch {
    status.value = 'error'
  }
}

onMounted(loadRecent)
</script>

<template>
  <main>
    <section class="hero">
      <div class="container hero__inner">
        <div class="hero__copy">
          <span class="eyebrow">Digital binder for TCG collectors</span>
          <h1 class="hero__title">Your Pokémon collection,<br />beautifully bound.</h1>
          <p class="hero__subtitle">
            Build binders for your Pokémon cards, arrange them your way, and share a
            read-only link so anyone can flip through your collection.
          </p>
          <div class="hero__actions">
            <router-link v-if="!isAuthenticated" to="/register" class="btn btn-primary">Start a binder</router-link>
            <router-link v-else to="/dashboard" class="btn btn-primary">Go to my binders</router-link>
            <router-link v-if="!isAuthenticated" to="/login" class="btn btn-ghost">Log in</router-link>
          </div>
        </div>
        <div class="hero__stack" aria-hidden="true">
          <span class="hero__card hero__card--1"></span>
          <span class="hero__card hero__card--2"></span>
          <span class="hero__card hero__card--3"></span>
        </div>
      </div>
    </section>

    <section class="container recent">
      <div class="recent__header">
        <h2>Recently shared binders</h2>
        <p class="recent__subtitle">A look at what collectors are putting together right now.</p>
      </div>

      <div v-if="status === 'loading'" class="binder-grid">
        <BinderCardSkeleton v-for="n in 8" :key="n" />
      </div>

      <ErrorState v-else-if="status === 'error'" @retry="loadRecent" message="Couldn't load recent binders." />

      <EmptyState
        v-else-if="status === 'empty'"
        title="No binders shared yet"
        message="Be the first collector to build a binder and share it with the world."
      >
        <router-link to="/register" class="btn btn-primary">Create the first binder</router-link>
      </EmptyState>

      <div v-else class="binder-grid">
        <BinderCard
          v-for="binder in recentBinders"
          :key="binder.id"
          :id="binder.id"
          :title="binder.title"
          :owner-label="ownerLabel(binder.owner_id)"
          :cover-images="binder.cover_images"
          :to="`/binders/${binder.id}`"
        />
      </div>
    </section>
  </main>
</template>

<style scoped>
.hero {
  border-bottom: 1px solid var(--color-border);
  background:
    radial-gradient(circle at 80% 0%, rgba(95, 208, 255, 0.08), transparent 55%),
    radial-gradient(circle at 10% 100%, rgba(245, 185, 66, 0.07), transparent 50%);
}
.hero__inner { display: flex; align-items: center; justify-content: space-between; gap: var(--space-7); padding: var(--space-8) var(--space-5); }
.hero__copy { max-width: 520px; display: flex; flex-direction: column; gap: var(--space-4); }
.hero__title { font-size: clamp(2rem, 4vw, 2.75rem); color: var(--color-text); }
.hero__subtitle { color: var(--color-text-muted); font-size: 1.02rem; max-width: 460px; }
.hero__actions { display: flex; gap: var(--space-3); margin-top: var(--space-2); flex-wrap: wrap; }

.hero__stack { position: relative; width: 220px; height: 280px; flex: none; }
.hero__card { position: absolute; width: 160px; height: 224px; border-radius: var(--radius-md); border: 1px solid var(--color-border-strong); box-shadow: var(--shadow-card); }
.hero__card--1 { background: #2A2440; top: 40px; left: 0; transform: rotate(-10deg); }
.hero__card--2 { background: #1F3A4A; top: 16px; left: 30px; transform: rotate(4deg); }
.hero__card--3 { background: var(--foil-gradient); top: 0; left: 60px; transform: rotate(-2deg); opacity: 0.92; }

.recent { padding: var(--space-8) var(--space-5); display: flex; flex-direction: column; gap: var(--space-5); }
.recent__header h2 { font-size: 1.4rem; color: var(--color-text); }
.recent__subtitle { color: var(--color-text-muted); margin-top: var(--space-1); }

.binder-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-5); }

@media (max-width: 760px) {
  .hero__inner { flex-direction: column; text-align: center; padding: var(--space-7) var(--space-4); }
  .hero__actions { justify-content: center; }
  .hero__stack { width: 180px; height: 220px; }
}
</style>
