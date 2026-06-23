import { apiFetch } from '../api/client'
import { authStore } from '../stores/auth'

export interface BinderSummary {
  id: string
  owner_id: string
  title: string
  description: string | null
  slug: string
  created_at: string
}

export interface BinderPublicSummary extends BinderSummary {
  cover_images: string[]
}

export interface CardSummary {
  id: string
  name: string
  images: { small: string; large: string }
}

export interface BinderCardEntry {
  position: number
  card: CardSummary
}

export interface BinderDetail extends BinderSummary {
  cards: BinderCardEntry[]
}

function authHeaders(): HeadersInit {
  const token = authStore.getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export const binderService = {
  async listRecentPublic(limit = 5): Promise<BinderPublicSummary[]> {
    return apiFetch<BinderPublicSummary[]>(`/binders/public/recent?limit=${limit}`)
  },
  async listMine(): Promise<BinderSummary[]> {
    return apiFetch<BinderSummary[]>('/binders', { headers: authHeaders() })
  },
  async get(id: string): Promise<BinderDetail> {
    return apiFetch<BinderDetail>(`/binders/${id}`, { headers: authHeaders() })
  },
  async create(title: string, description?: string): Promise<BinderSummary> {
    return apiFetch<BinderSummary>('/binders', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ title, description: description || null }),
    })
  },
  async remove(id: string): Promise<void> {
    await apiFetch<void>(`/binders/${id}`, { method: 'DELETE', headers: authHeaders() })
  },
  async update(id: string, cards: { card_id: string; position: number }[]): Promise<BinderDetail> {
    return apiFetch<BinderDetail>(`/binders/${id}`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ cards }),
    })
  },
}