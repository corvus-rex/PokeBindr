const TOKEN_KEY = 'pokebindr_token'

export const authStore = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },
  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  },
  clearToken(): void {
    localStorage.removeItem(TOKEN_KEY)
  },
  isAuthenticated(): boolean {
    return this.getToken() !== null
  },
}