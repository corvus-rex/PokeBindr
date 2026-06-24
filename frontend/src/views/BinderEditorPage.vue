<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { binderService } from '../services/binderService'
import { type CardSummary } from '../services/cardService'
import CardSearchPanel from '../components/CardSearchPanel.vue'
import ErrorState from '../components/ErrorState.vue'

const route = useRoute()
const binderId = route.params.id as string

const status = ref<'loading' | 'ready' | 'error'>('loading')
const isSaving = ref(false)
const saveError = ref<string | null>(null)
const binderTitle = ref('')
const hasUnsavedChanges = ref(false)

interface Slot {
  card: CardSummary | null
}

interface Page {
  slots: Slot[]
}

const pages = ref<Page[]>([])
const currentPageIndex = ref(0)

const currentPage = computed(() => pages.value[currentPageIndex.value] ?? null)
const totalPages = computed(() => pages.value.length)

const isDragActive = ref(false)
const dragOverSlotKey = ref<string | null>(null)
const dragIsFromBinder = ref(false)

function slotKey(pageIndex: number, slotIndex: number): string {
  return `${pageIndex}-${slotIndex}`
}

function setSlot(pageIndex: number, slotIndex: number, card: CardSummary | null) {
  if (pageIndex < 0 || pageIndex >= pages.value.length) return
  if (slotIndex < 0 || slotIndex >= 16) return
  pages.value[pageIndex].slots[slotIndex].card = card
  hasUnsavedChanges.value = true
}

function getSlot(pageIndex: number, slotIndex: number): CardSummary | null {
  if (pageIndex < 0 || pageIndex >= pages.value.length) return null
  if (slotIndex < 0 || slotIndex >= 16) return null
  return pages.value[pageIndex].slots[slotIndex].card
}

function parseDragData(raw: string): {
  type: 'search' | 'slot'
  card: CardSummary
  sourcePageIndex?: number
  sourceSlotIndex?: number
} | null {
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function onSearchDragStart() {
  isDragActive.value = true
  dragIsFromBinder.value = false
}

function onDragStartFromSlot(event: DragEvent, pageIndex: number, slotIndex: number) {
  const card = getSlot(pageIndex, slotIndex)
  if (!card) return
  event.dataTransfer?.setData(
    'text/plain',
    JSON.stringify({ type: 'slot', card, sourcePageIndex: pageIndex, sourceSlotIndex: slotIndex }),
  )
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
  }
  isDragActive.value = true
  dragIsFromBinder.value = true
}

function onDragOverSlot(event: DragEvent, pageIndex: number, slotIndex: number) {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = dragIsFromBinder.value ? 'move' : 'copy'
  }
  isDragActive.value = true
  dragOverSlotKey.value = slotKey(pageIndex, slotIndex)
}

function onDragLeaveSlot() {
  dragOverSlotKey.value = null
}

function onDropOnSlot(event: DragEvent, pageIndex: number, slotIndex: number) {
  event.preventDefault()
  event.stopPropagation()
  dragOverSlotKey.value = null
  isDragActive.value = false
  dragIsFromBinder.value = false

  const raw = event.dataTransfer?.getData('text/plain')
  if (!raw) return

  const data = parseDragData(raw)
  if (!data) return

  if (data.type === 'search') {
    setSlot(pageIndex, slotIndex, data.card)
  } else if (data.type === 'slot') {
    if (
      data.sourcePageIndex === pageIndex &&
      data.sourceSlotIndex === slotIndex
    ) return
    setSlot(data.sourcePageIndex!, data.sourceSlotIndex!, null)
    setSlot(pageIndex, slotIndex, data.card)
  }
}

function removeCardFromSlot(data: {
  type: 'search' | 'slot'
  card: CardSummary
  sourcePageIndex?: number
  sourceSlotIndex?: number
}) {
  if (data.type !== 'slot') return
  if (data.sourcePageIndex === undefined || data.sourceSlotIndex === undefined) return
  setSlot(data.sourcePageIndex, data.sourceSlotIndex, null)
}

function onDragOverBinder(event: DragEvent) {
  if (!dragIsFromBinder.value) return
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

function onDropOnBinder(event: DragEvent) {
  event.preventDefault()
  isDragActive.value = false
  dragIsFromBinder.value = false

  const raw = event.dataTransfer?.getData('text/plain')
  if (!raw) return

  const data = parseDragData(raw)
  if (!data) return

  removeCardFromSlot(data)
}

function onDragEnd() {
  isDragActive.value = false
  dragIsFromBinder.value = false
  dragOverSlotKey.value = null
}

function goToPrevPage() {
  if (currentPageIndex.value > 0) {
    currentPageIndex.value--
  }
}

function goToNextPage() {
  if (currentPageIndex.value < pages.value.length - 1) {
    currentPageIndex.value++
  } else {
    pages.value.push({ slots: Array.from({ length: 16 }, () => ({ card: null })) })
    currentPageIndex.value = pages.value.length - 1
  }
}

async function handleSave() {
  isSaving.value = true
  saveError.value = null
  try {
    const cards: { card_id: string; position: number }[] = []
    for (let pageIdx = 0; pageIdx < pages.value.length; pageIdx++) {
      const slots = pages.value[pageIdx].slots
      for (let slotIdx = 0; slotIdx < slots.length; slotIdx++) {
        const slot = slots[slotIdx]
        if (slot.card) {
          cards.push({
            card_id: slot.card.id,
            position: pageIdx * 16 + slotIdx,
          })
        }
      }
    }
    await binderService.update(binderId, cards)
    hasUnsavedChanges.value = false
  } catch {
    saveError.value = 'Failed to save changes. Try again.'
  } finally {
    isSaving.value = false
  }
}

async function loadBinder() {
  status.value = 'loading'
  try {
    const detail = await binderService.get(binderId)
    binderTitle.value = detail.title

    const pageMap = new Map<number, (CardSummary | null)[]>()
    for (const entry of detail.cards) {
      const pageIdx = Math.floor(entry.position / 16)
      const slotIdx = entry.position % 16
      if (!pageMap.has(pageIdx)) {
        pageMap.set(pageIdx, new Array(16).fill(null))
      }
      pageMap.get(pageIdx)![slotIdx] = entry.card
    }

    const maxPage = pageMap.size > 0 ? Math.max(...pageMap.keys()) : 0
    const result: Page[] = []
    for (let i = 0; i <= maxPage; i++) {
      const rawSlots = pageMap.get(i) ?? new Array(16).fill(null)
      result.push({ slots: rawSlots.map((c) => ({ card: c })) })
    }

    pages.value = result
    currentPageIndex.value = 0
    hasUnsavedChanges.value = false
    status.value = 'ready'
  } catch {
    status.value = 'error'
  }
}

onMounted(loadBinder)
</script>

<template>
  <main class="editor" @dragend="onDragEnd">
    <ErrorState
      v-if="status === 'error'"
      @retry="loadBinder"
      message="Couldn't load this binder. It may not exist."
    />

    <template v-else-if="status === 'loading'">
      <div class="editor__loading">
        <div class="shimmer editor__loading-block"></div>
        <div class="shimmer editor__loading-block editor__loading-block--wide"></div>
      </div>
    </template>

    <template v-else>
      <header class="editor__toolbar">
        <div class="editor__toolbar-left">
          <router-link
            :to="`/binders/${binderId}`"
            class="editor__back"
          >
            &larr; Binder
          </router-link>
          <h1 class="editor__title">{{ binderTitle }}</h1>
          <span
            v-if="hasUnsavedChanges"
            class="editor__unsaved"
          >
            Unsaved changes
          </span>
        </div>
        <div class="editor__toolbar-right">
          <p v-if="saveError" class="alert alert-danger editor__save-error">{{ saveError }}</p>
          <button
            class="btn btn-primary"
            :disabled="isSaving || !hasUnsavedChanges"
            @click="handleSave"
          >
            {{ isSaving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </header>

      <div class="editor__body">
        <div @dragstart="onSearchDragStart">
          <CardSearchPanel />
        </div>

        <div
          class="editor__binder"
          :class="{ 'editor__binder--remove-active': isDragActive && dragIsFromBinder }"
          @dragover="onDragOverBinder"
          @drop="onDropOnBinder"
        >
          <div class="editor__pagination" @dragover.stop @drop.stop>
            <button
              class="btn btn-ghost editor__page-btn"
              :disabled="currentPageIndex === 0"
              @click="goToPrevPage"
            >
              &larr; Prev
            </button>
            <span class="editor__page-indicator">
              Page {{ currentPageIndex + 1 }} of {{ totalPages }}
            </span>
            <button
              class="btn btn-ghost editor__page-btn"
              @click="goToNextPage"
            >
              Next &rarr;
            </button>
          </div>

          <div
            v-if="!currentPage"
            class="editor__empty-state"
          >
            <p>No pages</p>
          </div>

          <div
            v-else
            class="page-grid"
          >
            <div
              v-for="slotIndex in 16"
              :key="slotIndex - 1"
              class="slot"
              :class="{
                'slot--occupied': currentPage.slots[slotIndex - 1].card !== null,
                'slot--dragover': dragOverSlotKey === slotKey(currentPageIndex, slotIndex - 1),
                'slot--drag-active': isDragActive,
              }"
              @dragover="onDragOverSlot($event, currentPageIndex, slotIndex - 1)"
              @dragleave="onDragLeaveSlot"
              @drop="onDropOnSlot($event, currentPageIndex, slotIndex - 1)"
            >
              <template v-if="currentPage.slots[slotIndex - 1].card">
                <img
                  :src="currentPage.slots[slotIndex - 1].card!.images.small"
                  :alt="currentPage.slots[slotIndex - 1].card!.name"
                  class="slot__image"
                  draggable="true"
                  @dragstart="onDragStartFromSlot($event, currentPageIndex, slotIndex - 1)"
                />
              </template>
              <span v-else class="slot__empty-label">Empty</span>
            </div>
          </div>

          <div
            v-if="isDragActive && dragIsFromBinder"
            class="editor__remove-hint"
          >
            Drop outside the grid to remove card
          </div>
        </div>
      </div>
    </template>
  </main>
</template>

<style scoped>
.editor {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor__loading {
  padding: var(--space-7) var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-width: 480px;
}

.shimmer {
  background: linear-gradient(
    100deg,
    var(--color-surface-raised) 30%,
    var(--color-border) 50%,
    var(--color-surface-raised) 70%
  );
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
  border-radius: var(--radius-md);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.editor__loading-block {
  height: 32px;
  width: 240px;
}

.editor__loading-block--wide {
  width: 360px;
  height: 200px;
}

.editor__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
  flex-wrap: wrap;
}

.editor__toolbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  min-width: 0;
}

.editor__toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.editor__back {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  flex: none;
  transition: color 0.12s ease;
}

.editor__back:hover {
  color: var(--color-text);
}

.editor__title {
  font-size: 1.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.editor__unsaved {
  font-size: 0.75rem;
  font-family: var(--font-mono);
  color: var(--color-accent);
  background: rgba(245, 185, 66, 0.12);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  flex: none;
}

.editor__save-error {
  font-size: 0.82rem;
  padding: var(--space-2) var(--space-3);
}

.editor__body {
  flex: 1;
  display: flex;
  gap: var(--space-5);
  padding: var(--space-5);
  overflow: auto;
}

.editor__binder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-5);
  min-width: 0;
  border-radius: var(--radius-lg);
  border: 2px solid transparent;
  transition: border-color 0.15s ease, background 0.15s ease;
  padding: var(--space-3);
  margin: calc(var(--space-3) * -1);
}

.editor__binder--remove-active {
  border-color: var(--color-danger);
  background: rgba(226, 87, 76, 0.04);
}

.editor__pagination {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.editor__page-btn {
  font-size: 0.85rem;
  padding: var(--space-2) var(--space-4);
}

.editor__page-indicator {
  font-family: var(--font-mono);
  font-size: 0.88rem;
  color: var(--color-text-muted);
  min-width: 100px;
  text-align: center;
}

.editor__empty-state {
  padding: var(--space-7);
  color: var(--color-text-faint);
}

.page-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
  width: 100%;
  max-width: 520px;
}

.slot {
  aspect-ratio: 5 / 7;
  background: var(--color-surface);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.12s ease, background 0.12s ease, transform 0.12s ease;
  position: relative;
  overflow: hidden;
}

.slot--occupied {
  border-style: solid;
  border-color: var(--color-border-strong);
  background: var(--color-bg-elevated);
}

.slot--drag-active {
  border-color: var(--color-border-strong);
}

.slot--dragover {
  border-color: var(--color-accent);
  background: rgba(245, 185, 66, 0.08);
  transform: scale(1.04);
}

.slot__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  cursor: grab;
  user-select: none;
}

.slot__image:active {
  cursor: grabbing;
}

.slot__empty-label {
  font-size: 0.72rem;
  color: var(--color-text-faint);
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  user-select: none;
}

.editor__remove-hint {
  font-size: 0.82rem;
  font-family: var(--font-mono);
  color: var(--color-danger);
  padding: var(--space-2) var(--space-4);
  border: 1px dashed var(--color-danger);
  border-radius: var(--radius-sm);
  background: rgba(226, 87, 76, 0.06);
  text-align: center;
  pointer-events: none;
  user-select: none;
}

@media (max-width: 800px) {
  .editor__body {
    flex-direction: column;
    align-items: stretch;
  }

  .page-grid {
    max-width: 100%;
    gap: var(--space-2);
  }

  .editor__binder--remove-active {
    border-color: transparent;
    background: rgba(226, 87, 76, 0.06);
  }
}
</style>
