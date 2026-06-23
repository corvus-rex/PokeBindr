
<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '../services/authService'
import { ApiError } from '../api/client'

const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const isSubmitting = ref(false)

const route = useRoute()
const router = useRouter()

async function handleSubmit() {
  error.value = null
  isSubmitting.value = true
  try {
    await authService.login(email.value, password.value)
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
  } catch (err) {
    error.value = err instanceof ApiError ? err.detail : 'Login failed'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <div class="auth-card panel">
      <span class="eyebrow">Welcome back</span>
      <h1>Log in</h1>
      <form @submit.prevent="handleSubmit" class="auth-form">
        <label class="field">
          Email
          <input v-model="email" type="email" required autocomplete="email" />
        </label>
        <label class="field">
          Password
          <input v-model="password" type="password" required autocomplete="current-password" />
        </label>
        <p v-if="error" class="alert alert-danger">{{ error }}</p>
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Logging in…' : 'Log in' }}
        </button>
      </form>
      <p class="auth-card__footer">No account? <router-link to="/register">Register</router-link></p>
    </div>
  </main>
</template>

<style scoped>
.auth-page { flex: 1; display: flex; align-items: center; justify-content: center; padding: var(--space-6) var(--space-5); }
.auth-card { width: 100%; max-width: 380px; padding: var(--space-6); display: flex; flex-direction: column; gap: var(--space-4); }
.auth-card h1 { font-size: 1.5rem; }
.auth-form { display: flex; flex-direction: column; gap: var(--space-4); }
.auth-card__footer { color: var(--color-text-muted); font-size: 0.9rem; text-align: center; }
.auth-card__footer a { color: var(--color-accent-blue); }
</style>