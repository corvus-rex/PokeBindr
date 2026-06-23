import { ref } from 'vue'

const TOKEN_KEY = 'pokebindr_token'
const tokenRef = ref<string | null>(localStorage.getItem(TOKEN_KEY))

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
    return tokenRef.value !== null
  },
  getUserId(): string | null {
    const token = tokenRef.value
    if (!token) return null
    try {
      const payload = token.split('.')[1]
      const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
      return JSON.parse(atob(base64)).sub as string
    } catch {
      return null
    }
  },
}