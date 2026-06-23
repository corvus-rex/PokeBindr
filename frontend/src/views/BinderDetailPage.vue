<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { binderService, type BinderDetail } from '../services/binderService'
import { authStore } from '../stores/auth'
import ErrorState from '../components/ErrorState.vue'
import EmptyState from '../components/EmptyState.vue'

const route = useRoute()
const status = ref<'loading' | 'ready' | 'error'>('loading')
const binder = ref<BinderDetail | null>(null)
const isAuthenticated = computed(() => authStore.isAuthenticated())

function ownerLabel(ownerId: string): string {
  return `Collector #${ownerId.slice(-6).toUpperCase()}`
}

async function load() {
  status.value = 'loading'
  try {
    binder.value = await binderService.get(route.params.id as string)
    status.value = 'ready'
  } catch {
    status.value = 'error'
  }
}

onMounted(load)
</script>

<template>
  <main class="container binder-page">
    <p v-if="status === 'loading'" class="binder-page__loading">Loading binder…</p>
    <ErrorState v-else-if="status === 'error'" @retry="load" message="Couldn't load this binder. It may not exist." />

    <template v-else-if="binder">
      <header class="binder-page__header">
        <div class="binder-page__title-row">
          <div>
            <span class="eyebrow">Binder</span>
            <h1>{{ binder.title }}</h1>
          </div>
          <router-link
            v-if="isAuthenticated"
            :to="`/binders/${binder.id}/edit`"
            class="btn btn-primary binder-page__edit-btn"
          >
            Edit cards
          </router-link>
        </div>
        <p v-if="binder.description" class="binder-page__description">{{ binder.description }}</p>
        <span class="binder-page__owner">by {{ ownerLabel(binder.owner_id) }}</span>
      </header>

      <EmptyState
        v-if="binder.cards.length === 0"
        title="This binder is empty"
        message="No cards have been added to this binder yet."
      />

      <div v-else class="card-grid">
        <figure v-for="entry in binder.cards" :key="entry.position" class="card-tile">
          <img :src="entry.card.images.small" :alt="entry.card.name" />
          <figcaption>{{ entry.card.name }}</figcaption>
        </figure>
      </div>
    </template>
  </main>
</template>

<style scoped>
.binder-page { padding: var(--space-7) var(--space-5); display: flex; flex-direction: column; gap: var(--space-6); }
.binder-page__loading { color: var(--color-text-muted); padding: var(--space-7) 0; }
.binder-page__header { display: flex; flex-direction: column; gap: var(--space-2); border-bottom: 1px solid var(--color-border); padding-bottom: var(--space-5); }
.binder-page__title-row { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-4); }
.binder-page__header h1 { font-size: 1.8rem; }
.binder-page__edit-btn { font-size: 0.85rem; padding: var(--space-2) var(--space-4); flex: none; }
.binder-page__description { color: var(--color-text-muted); max-width: 540px; }
.binder-page__owner { font-family: var(--font-mono); font-size: 0.78rem; color: var(--color-text-faint); }

.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: var(--space-4); }
.card-tile { margin: 0; display: flex; flex-direction: column; gap: var(--space-2); background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: var(--space-3); }
.card-tile img { width: 100%; border-radius: var(--radius-sm); }
.card-tile figcaption { font-size: 0.82rem; text-align: center; color: var(--color-text-muted); }
</style>