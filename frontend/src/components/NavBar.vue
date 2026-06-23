<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authStore } from '../stores/auth'
import { authService } from '../services/authService'

const route = useRoute()
const router = useRouter()

const isAuthenticated = computed(() => authStore.isAuthenticated())

function isActive(name: string): boolean {
  return route.name === name
}

function handleLogout() {
  authService.logout()
  router.push('/login')
}
</script>

<template>
  <header class="navbar">
    <div class="container navbar__inner">
      <router-link to="/" class="navbar__brand">
        <span class="navbar__mark" aria-hidden="true">
          <span class="navbar__mark-card navbar__mark-card--back"></span>
          <span class="navbar__mark-card navbar__mark-card--front"></span>
        </span>
        <span class="navbar__wordmark">Poke<strong>Bindr</strong></span>
      </router-link>

      <nav class="navbar__links">
        <router-link to="/" class="navbar__link" :class="{ 'navbar__link--active': isActive('landing') }">
          Home
        </router-link>
        <router-link
          v-if="isAuthenticated"
          to="/dashboard"
          class="navbar__link"
          :class="{ 'navbar__link--active': isActive('dashboard') }"
        >
          My Binders
        </router-link>
        <template v-if="!isAuthenticated">
          <router-link to="/login" class="navbar__link" :class="{ 'navbar__link--active': isActive('login') }">
            Log In
          </router-link>
          <router-link to="/register" class="btn btn-primary navbar__cta">Register</router-link>
        </template>
        <button v-else class="btn btn-ghost navbar__cta" @click="handleLogout">Log Out</button>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 20;
  background: rgba(15, 17, 21, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border);
}
.navbar__inner { display: flex; align-items: center; justify-content: space-between; height: 64px; gap: var(--space-5); }

.navbar__brand { display: flex; align-items: center; gap: var(--space-3); font-family: var(--font-display); font-size: 1.05rem; color: var(--color-text); }
.navbar__wordmark strong { color: var(--color-accent); font-weight: 700; }

.navbar__mark { position: relative; width: 26px; height: 22px; flex: none; }
.navbar__mark-card { position: absolute; width: 16px; height: 22px; border-radius: 3px; border: 1.5px solid var(--color-border-strong); }
.navbar__mark-card--back { left: 0; top: 2px; background: var(--color-surface-raised); transform: rotate(-8deg); }
.navbar__mark-card--front { left: 8px; top: 0; background: var(--foil-gradient); transform: rotate(6deg); }

.navbar__links { display: flex; align-items: center; gap: var(--space-5); }
.navbar__link { font-size: 0.92rem; color: var(--color-text-muted); padding: var(--space-2) 0; border-bottom: 2px solid transparent; transition: color 0.12s ease, border-color 0.12s ease; }
.navbar__link:hover { color: var(--color-text); }
.navbar__link--active { color: var(--color-text); border-bottom-color: var(--color-accent); }
.navbar__cta { padding: var(--space-2) var(--space-4); font-size: 0.88rem; }

@media (max-width: 640px) {
  .navbar__inner { gap: var(--space-3); }
  .navbar__links { gap: var(--space-3); }
  .navbar__link { font-size: 0.85rem; }
}
</style>