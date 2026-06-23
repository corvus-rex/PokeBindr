<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { binderService, type BinderDetail, type BinderSummary } from '../services/binderService'
import BinderCard from '../components/BinderCard.vue'
import BinderCardSkeleton from '../components/BinderCardSkeleton.vue'
import EmptyState from '../components/EmptyState.vue'
import ErrorState from '../components/ErrorState.vue'

interface BinderWithCover extends BinderSummary {
  coverImages: string[]
}

const status = ref<'loading' | 'ready' | 'empty' | 'error'>('loading')
const binders = ref<BinderWithCover[]>([])

const showCreate = ref(false)
const newTitle = ref('')
const newDescription = ref('')
const createError = ref<string | null>(null)
const isCreating = ref(false)

async function loadBinders() {
  status.value = 'loading'
  try {
    const mine = await binderService.listMine()
    const recent = [...mine]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5)

    const withCovers = await Promise.all(
      recent.map(async (b) => {
        try {
          const detail: BinderDetail = await binderService.get(b.id)
          return { ...b, coverImages: detail.cards.slice(0, 3).map((c) => c.card.images.small) }
        } catch {
          return { ...b, coverImages: [] }
        }
      }),
    )

    binders.value = withCovers
    status.value = withCovers.length === 0 ? 'empty' : 'ready'
  } catch {
    status.value = 'error'
  }
}

async function handleCreate() {
  createError.value = null
  isCreating.value = true
  try {
    await binderService.create(newTitle.value, newDescription.value)
    newTitle.value = ''
    newDescription.value = ''
    showCreate.value = false
    await loadBinders()
  } catch {
    createError.value = 'Could not create the binder. Try again.'
  } finally {
    isCreating.value = false
  }
}

async function handleDelete(id: string) {
  if (!confirm('Delete this binder? This cannot be undone.')) return
  await binderService.remove(id)
  await loadBinders()
}

onMounted(loadBinders)
</script>

<template>
  <main class="container dashboard">
    <div class="dashboard__header">
      <div>
        <h1>My binders</h1>
        <p class="dashboard__subtitle">Your most recently created binders.</p>
      </div>
      <button class="btn btn-primary" @click="showCreate = true">+ Create binder</button>
    </div>

    <div v-if="status === 'loading'" class="binder-grid">
      <BinderCardSkeleton v-for="n in 5" :key="n" />
    </div>

    <ErrorState v-else-if="status === 'error'" @retry="loadBinders" message="Couldn't load your binders." />

    <EmptyState
      v-else-if="status === 'empty'"
      title="You haven't created a binder yet"
      message="Start a binder to begin organizing and sharing your Pokémon cards."
    >
      <button class="btn btn-primary" @click="showCreate = true">Create your first binder</button>
    </EmptyState>

    <div v-else class="binder-grid">
      <BinderCard
        v-for="binder in binders"
        :key="binder.id"
        :id="binder.id"
        :title="binder.title"
        owner-label="You"
        :cover-images="binder.coverImages"
        :to="`/binders/${binder.id}`"
      >
        <template #actions>
          <button class="binder-card__delete" title="Delete binder" @click.stop.prevent="handleDelete(binder.id)">×</button>
        </template>
      </BinderCard>
    </div>

    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal panel">
        <h2>Create a binder</h2>
        <form @submit.prevent="handleCreate" class="modal__form">
          <label class="field">
            Title
            <input v-model="newTitle" required maxlength="80" placeholder="Kanto Favorites" />
          </label>
          <label class="field">
            Description (optional)
            <textarea v-model="newDescription" rows="3" maxlength="240" placeholder="What's this binder about?"></textarea>
          </label>
          <p v-if="createError" class="alert alert-danger">{{ createError }}</p>
          <div class="modal__actions">
            <button type="button" class="btn btn-ghost" @click="showCreate = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isCreating">
              {{ isCreating ? 'Creating…' : 'Create binder' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>

<style scoped>
.dashboard { padding: var(--space-7) var(--space-5); display: flex; flex-direction: column; gap: var(--space-5); }
.dashboard__header { display: flex; align-items: flex-end; justify-content: space-between; gap: var(--space-4); flex-wrap: wrap; }
.dashboard__header h1 { font-size: 1.6rem; }
.dashboard__subtitle { color: var(--color-text-muted); margin-top: var(--space-1); }

.binder-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-5); }

.binder-card__delete {
  width: 28px; height: 28px;
  border-radius: 50%;
  border: 1px solid var(--color-border-strong);
  background: var(--color-bg-elevated);
  color: var(--color-text-muted);
  font-size: 1rem;
  line-height: 1;
  cursor: pointer;
}
.binder-card__delete:hover { color: var(--color-danger); border-color: var(--color-danger); }

.modal-overlay { position: fixed; inset: 0; background: rgba(8, 9, 12, 0.7); display: flex; align-items: center; justify-content: center; padding: var(--space-5); z-index: 50; }
.modal { width: 100%; max-width: 420px; padding: var(--space-6); display: flex; flex-direction: column; gap: var(--space-4); }
.modal__form { display: flex; flex-direction: column; gap: var(--space-4); }
.modal__actions { display: flex; justify-content: flex-end; gap: var(--space-3); }
</style>