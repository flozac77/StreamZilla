<template>
  <div :class="[
    'transition-all duration-500 ease-in-out',
    { 'translate-y-0': !hasSearched, '-translate-y-1/2': hasSearched }
  ]">
    <div class="relative max-w-xl mx-auto">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Rechercher un jeu..."
        :disabled="videoStore.loading"
        :class="[
          'w-full px-4 py-3 text-lg bg-white text-gray-800 rounded-lg border focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent',
          {
            'border-red-500': videoStore.error,
            'border-gray-300': !videoStore.error,
            'opacity-50 cursor-not-allowed': videoStore.loading
          }
        ]"
        @keyup.enter="handleSearch"
      />
      <button
        @click="handleSearch"
        :disabled="videoStore.loading || !searchQuery.trim()"
        :class="[
          'absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 rounded-md transition-colors',
          {
            'bg-twitch-purple text-white hover:bg-opacity-90': !videoStore.loading && searchQuery.trim(),
            'bg-gray-300 text-gray-500 cursor-not-allowed': videoStore.loading || !searchQuery.trim()
          }
        ]"
      >
        {{ videoStore.loading ? 'Recherche...' : 'Rechercher' }}
      </button>
    </div>
    <p v-if="videoStore.error" class="text-red-500 text-sm mt-2 text-center">
      {{ videoStore.error }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useVideoStore } from '@/stores/videoStore'
import { useDebounceFn } from '@vueuse/core'

const videoStore = useVideoStore()
const searchQuery = ref('')
const hasSearched = ref(false)

const search = async (query: string) => {
  if (!query.trim()) return
  
  try {
    await videoStore.searchVideosByGame(query.trim())
    hasSearched.value = true
  } catch (error) {
    // L'erreur est déjà gérée dans le store
    console.error('Erreur lors de la recherche:', error)
  }
}

// useDebounceFn accepte une fonction et un délai en ms
const debouncedSearch = useDebounceFn((query: string) => {
  search(query)
}, 500)

watch(searchQuery, (newValue) => {
  if (!newValue.trim()) {
    videoStore.resetSearch()
    hasSearched.value = false
    return
  }
  
  debouncedSearch(newValue)
})

const handleSearch = () => {
  if (videoStore.loading) return
  search(searchQuery.value)
}
</script> 