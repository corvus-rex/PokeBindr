import { apiFetch } from '../api/client'

export interface CardSummary {
  id: string
  name: string
  images: { small: string; large: string }
}

interface CardSearchResult {
  total: number
  page: number
  page_size: number
  results: CardSummary[]
}

export const cardService = {
  async search(name: string, page = 1, pageSize = 50): Promise<CardSummary[]> {
    const params = new URLSearchParams()
    params.set('name', name)
    params.set('page', String(page))
    params.set('page_size', String(pageSize))
    const result = await apiFetch<CardSearchResult>(`/cards/search?${params}`)
    return result.results
  },
}
