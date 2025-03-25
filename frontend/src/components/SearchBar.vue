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
        class="w-full px-4 py-3 text-lg bg-twitch-light text-twitch-text rounded-lg border border-gray-700 focus:outline-none focus:border-twitch-purple"
        @keyup.enter="handleSearch"
      />
      <button
        @click="handleSearch"
        class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-twitch-purple text-white px-4 py-2 rounded-md hover:bg-opacity-90 transition-colors"
      >
        Rechercher
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useVideoStore } from '../stores/videoStore'
import { useDebounceFn } from '@vueuse/core'

const videoStore = useVideoStore()
const searchQuery = ref('')
const hasSearched = ref(false)

const debouncedSearch = useDebounceFn((query) => {
  if (query.trim()) {
    videoStore.searchVideos(query)
    hasSearched.value = true
  }
}, 500)

watch(searchQuery, (newValue) => {
  if (newValue.trim()) {
    debouncedSearch(newValue)
  } else {
    videoStore.resetSearch()
    hasSearched.value = false
  }
})

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    videoStore.searchVideos(searchQuery.value)
    hasSearched.value = true
  }
}
</script> 