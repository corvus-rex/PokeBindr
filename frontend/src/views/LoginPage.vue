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
    <h1>Log In</h1>
    <form @submit.prevent="handleSubmit">
      <label>
        Email
        <input v-model="email" type="email" required />
      </label>
      <label>
        Password
        <input v-model="password" type="password" required />
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" :disabled="isSubmitting">Log In</button>
    </form>
    <p>
      No account? <router-link to="/register">Register</router-link>
    </p>
  </main>
</template>

<style scoped>
.auth-page {
  max-width: 360px;
  margin: 4rem auto;
  font-family: sans-serif;
}
form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.error {
  color: #c0392b;
}
</style>