<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserPreferencesStore } from './stores/userPreferences'

// On n'a plus besoin d'importer createPinia car il est configuré dans main.ts
// On n'a plus besoin d'importer SearchBar et VideoGrid car ils sont utilisés dans les vues
// On n'a plus besoin d'importer useVideoStore car il n'est pas utilisé directement ici

const userPreferences = useUserPreferencesStore()

onMounted(() => {
  userPreferences.loadFromLocalStorage()
})
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <nav class="bg-gray-800 shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="text-xl font-bold">VisioBrain</router-link>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <router-view></router-view>
    </main>
  </div>
</template>

<style>
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  padding: 0;
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
