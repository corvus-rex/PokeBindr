<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/authService'
import { ApiError } from '../api/client'

const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const isSubmitting = ref(false)

const router = useRouter()

async function handleSubmit() {
  error.value = null
  isSubmitting.value = true
  try {
    await authService.register(email.value, password.value)
    router.push('/login')
  } catch (err) {
    error.value = err instanceof ApiError ? err.detail : 'Registration failed'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <h1>Register</h1>
    <form @submit.prevent="handleSubmit">
      <label>
        Email
        <input v-model="email" type="email" required />
      </label>
      <label>
        Password
        <input v-model="password" type="password" required minlength="8" />
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" :disabled="isSubmitting">Register</button>
    </form>
    <p>
      Already have an account? <router-link to="/login">Log In</router-link>
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