<script setup lang="ts">
import { useRouter } from 'vue-router'
import { authService } from '../services/authService'

const router = useRouter()

function handleLogout() {
  authService.logout()
  router.push('/login')
}
</script>

<template>
  <main>
    <h1>Dashboard</h1>
    <p>You are logged in.</p>
    <button @click="handleLogout">Log Out</button>
  </main>
</template>