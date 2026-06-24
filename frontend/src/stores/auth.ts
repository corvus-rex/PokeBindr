import { ref } from 'vue'

const TOKEN_KEY = 'pokebindr_token'
const tokenRef = ref<string | null>(localStorage.getItem(TOKEN_KEY))

function decodePayload(token: string): Record<string, unknown> | null {
  try {
    const payload = token.split('.')[1]
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(base64))
  } catch {
    return null
  }
}

function isTokenExpired(token: string): boolean {
  const payload = decodePayload(token)
  if (!payload) return true
  const exp = payload.exp as number | undefined
  if (!exp) return true
  return Date.now() >= exp * 1000
}

export const authStore = {
  getToken(): string | null {
    return tokenRef.value
  },
  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
    tokenRef.value = token
  },
  clearToken(): void {
    localStorage.removeItem(TOKEN_KEY)
    tokenRef.value = null
  },
  isAuthenticated(): boolean {
    return tokenRef.value !== null && !isTokenExpired(tokenRef.value)
  },
  getUserId(): string | null {
    const token = tokenRef.value
    if (!token) return null
    const payload = decodePayload(token)
    return payload?.sub as string | null ?? null
  },
}