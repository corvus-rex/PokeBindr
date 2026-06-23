<script setup lang="ts">
import { ref } from 'vue'
import { cardService, type CardSummary } from '../services/cardService'

const query = ref('')
const results = ref<CardSummary[]>([])
const isSearching = ref(false)
const hasSearched = ref(false)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

async function performSearch(q: string) {
  if (!q.trim()) {
    results.value = []
    hasSearched.value = false
    return
  }
  isSearching.value = true
  hasSearched.value = true
  try {
    results.value = await cardService.search(q.trim())
  } catch {
    results.value = []
  } finally {
    isSearching.value = false
  }
}

function onInput(value: string) {
  query.value = value
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => performSearch(value), 300)
}

function onDragStart(event: DragEvent, card: CardSummary) {
  event.dataTransfer?.setData(
    'text/plain',
    JSON.stringify({ type: 'search', card }),
  )
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'copy'
  }
}
</script>

<template>
  <div class="search-panel">
    <div class="search-panel__header">
      <h3 class="search-panel__title">Search cards</h3>
    </div>
    <div class="search-panel__input-wrapper">
      <input
        :value="query"
        type="search"
        placeholder="Search by name…"
        class="search-panel__input"
        @input="onInput(($event.target as HTMLInputElement).value)"
      />
    </div>
    <div class="search-panel__results">
      <div v-if="isSearching" class="search-panel__loading">
        <span class="shimmer-line"></span>
        <span class="shimmer-line"></span>
        <span class="shimmer-line"></span>
      </div>
      <p
        v-else-if="hasSearched && results.length === 0 && query.trim()"
        class="search-panel__empty"
      >
        No cards found
      </p>
      <template v-else>
        <div
          v-for="card in results"
          :key="card.id"
          class="search-card"
          draggable="true"
          @dragstart="onDragStart($event, card)"
        >
          <img
            :src="card.images.small"
            :alt="card.name"
            class="search-card__image"
            loading="lazy"
          />
          <span class="search-card__name">{{ card.name }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.search-panel {
  width: 220px;
  flex: none;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.search-panel__header {
  padding: var(--space-4) var(--space-4) 0;
}

.search-panel__title {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.search-panel__input-wrapper {
  padding: var(--space-3) var(--space-4);
}

.search-panel__input {
  width: 100%;
  font-family: var(--font-body);
  font-size: 0.9rem;
  color: var(--color-text);
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-3);
  outline: none;
  transition: border-color 0.12s ease;
}

.search-panel__input:focus {
  border-color: var(--color-accent-blue);
}

.search-panel__input::placeholder {
  color: var(--color-text-faint);
}

.search-panel__results {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-4) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  max-height: 480px;
}

.search-panel__loading {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-3) 0;
}

.shimmer-line {
  height: 40px;
  border-radius: var(--radius-sm);
  background: linear-gradient(
    100deg,
    var(--color-surface-raised) 30%,
    var(--color-border) 50%,
    var(--color-surface-raised) 70%
  );
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.search-panel__empty {
  color: var(--color-text-faint);
  font-size: 0.85rem;
  text-align: center;
  padding: var(--space-5) 0;
}

.search-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  cursor: grab;
  transition: border-color 0.12s ease, background 0.12s ease;
  user-select: none;
}

.search-card:hover {
  border-color: var(--color-border-strong);
  background: var(--color-surface-raised);
}

.search-card:active {
  cursor: grabbing;
}

.search-card__image {
  width: 40px;
  height: auto;
  aspect-ratio: 5 / 7;
  border-radius: 3px;
  flex: none;
}

.search-card__name {
  font-size: 0.82rem;
  color: var(--color-text);
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

@media (max-width: 800px) {
  .search-panel {
    width: 100%;
    max-height: 260px;
  }

  .search-panel__results {
    max-height: 180px;
  }
}
</style>
