import { apiFetch } from '../api/client'
import { authStore } from '../stores/auth'

interface TokenResponse {
  access_token: string
  token_type: string
}

interface UserResponse {
  id: string
  email: string
  created_at: string
}

export const authService = {
  async register(email: string, password: string): Promise<UserResponse> {
    return apiFetch<UserResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  },

  async login(email: string, password: string): Promise<void> {
    const result = await apiFetch<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    authStore.setToken(result.access_token)
  },

  logout(): void {
    authStore.clearToken()
  },
}