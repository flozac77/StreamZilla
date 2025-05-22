<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Search bar -->
    <div class="mb-8">
      <input
        type="text"
        v-model="searchQuery"
        @keyup.enter="handleSearch"
        placeholder="Search for a game..."
        class="w-full bg-gray-700 text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
        data-test="search-input"
      />
    </div>

    <!-- Filters -->
    <SearchFilters
      @update:filters="updateFilters"
      @update:sort="updateSort"
    />

    <div v-if="loading" class="flex justify-center items-center h-64">
      <LoadingSpinner message="Loading videos..." />
    </div>
    
    <div v-else-if="error" class="text-center text-red-500">
      {{ error }}
      <button @click="retrySearch" class="ml-2 text-blue-500 hover:underline">
        Retry
      </button>
    </div>
    
    <div v-else>
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-white">
          {{ game }} Videos
        </h1>
        <button
          @click="toggleFavoriteWithNotification(game)"
          :class="[
            'px-4 py-2 rounded-lg flex items-center gap-2 transition-colors',
            isFavorite(game)
              ? 'bg-purple-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          ]"
        >
          <span class="material-icons">
            {{ isFavorite(game) ? 'favorite' : 'favorite_border' }}
          </span>
          {{ isFavorite(game) ? 'Remove from favorites' : 'Add to favorites' }}
        </button>
      </div>

      <!-- User Preferences Component -->
      <UserPreferences class="mb-8" />
      
      <!-- Video Grid -->
      <div v-if="videoStore.visibleVideos.length === 0" class="text-center text-gray-500">
        No videos found
      </div>
      
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-test="video-grid">
        <div v-for="(video, index) in videoStore.visibleVideos" 
             :key="`${video.id}-${video.user_name}-${index}`"
             class="bg-gray-800 rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300"
             data-test="video-card">
          <VideoThumbnail 
            :username="video.user_name"
            :alt="video.title"
          >
            <template #overlay>
              <span class="bg-purple-600 px-2 py-1 rounded text-sm">
                {{ formatDurationForDisplay(video.duration) }}
              </span>
            </template>
          </VideoThumbnail>
          
          <div class="p-4">
            <h2 class="text-xl font-semibold mb-2 line-clamp-2 text-white">{{ video.title }}</h2>
            <p class="text-purple-400 mb-2">{{ video.user_name }}</p>
            <p class="text-gray-400 text-sm">{{ formatViews(video.view_count) }} views • {{ formatDurationForDisplay(video.duration) }}</p>
          </div>
          
          <div class="px-4 pb-4">
            <a :href="video.url" 
               target="_blank"
               class="inline-block bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors duration-300">
              Watch on Twitch
            </a>
          </div>
        </div>
      </div>

      <!-- Loader and infinite scroll trigger -->
      <div ref="loadMoreTrigger" 
           class="flex justify-center py-8 mt-4">
        <template v-if="videoStore.loading || videoStore.loadingMore">
          <LoadingSpinner :message="videoStore.loadingMore ? 'Loading more videos...' : 'Loading videos...'" />
        </template>
        <template v-else-if="!videoStore.hasMore && videoStore.visibleVideos.length > 0">
          <p class="text-gray-500">No more videos available</p>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, defineExpose } from 'vue'
import { useRoute } from 'vue-router'
import { useVideoStore } from '@/stores/video'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import SearchFilters from '@/components/SearchFilters.vue'
import UserPreferences from '@/components/UserPreferences.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import VideoThumbnail from '@/components/VideoThumbnail.vue'
import { useIntersectionObserver } from '@vueuse/core'
import { useToast } from 'vue-toastification'
import type { FilterChangeEvent, SortOption } from '@/types/filters'
import axios from 'axios'
import { formatViews, formatDurationForDisplay } from '@/utils/formatters'

const route = useRoute()
const videoStore = useVideoStore()
const userPreferences = useUserPreferencesStore()
const toast = useToast()
const loadMoreTrigger = ref<HTMLElement | null>(null)
const { toggleFavorite, isFavorite, addToHistory } = userPreferences

const game = ref(route.params.game as string)
const loading = ref(false)
const error = ref('')
const refreshInterval = ref<number | null>(null)
const searchQuery = ref(game.value || '')

const handleSearch = () => {
  // Trimming is now handled by the store's searchVideosByGame action
  if (searchQuery.value) { // Store will handle if it's all whitespace
    game.value = searchQuery.value 
    fetchVideos()
  } else {
    // If search query is completely empty, might want to reset or do nothing
    // The store's searchVideosByGame will also handle empty string by resetting.
    videoStore.resetState() // Or rely on the store's handling
  }
}

const updateFilters = (event: FilterChangeEvent) => {
  console.log('VideoListView - updateFilters:', event)
  videoStore.updateFilters(event)
}

const updateSort = (sortBy: SortOption) => {
  console.log('VideoListView - updateSort:', sortBy)
  videoStore.updateSort(sortBy)
}

// Configuration de l'Intersection Observer avec des options plus sensibles
const setupIntersectionObserver = () => {
  if (!loadMoreTrigger.value) return

  const observer = useIntersectionObserver(
    loadMoreTrigger,
    ([entry]) => {
      if (entry.isIntersecting && !videoStore.loading && !videoStore.loadingMore && videoStore.hasMore) {
        console.log('🔄 Intersection detected, loading more videos...')
        videoStore.loadMore()
      }
    },
    {
      threshold: 0.1,
      rootMargin: '200px'
    }
  )

  return observer
}

// Gestion du chargement initial
const fetchVideos = async () => {
  try {
    loading.value = true
    error.value = ''
    console.log('Starting search for:', game.value)
    await videoStore.searchVideosByGame(game.value)
    addToHistory(game.value)
  } catch (e) {
    console.error('Detailed error in fetchVideos:', e)
    if (axios.isAxiosError(e) && e.response) {
      error.value = `Error: ${e.response.data.message || 'An error occurred while loading videos'}`
    } else {
      error.value = "An error occurred while loading videos"
    }
    toast.error(error.value)
  } finally {
    loading.value = false
  }
}

// Réessayer en cas d'erreur
const retrySearch = () => {
  fetchVideos()
}

// Initialisation
onMounted(() => {
  fetchVideos()
  setupIntersectionObserver()
  startAutoRefresh()
})

// Configuration du rechargement automatique
const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshInterval.value = window.setInterval(() => {
    console.log('Auto-refreshing videos...')
    fetchVideos()
  }, 120000)
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// Réinitialisation lors du changement de jeu
watch(() => route.params.game, (newGame) => {
  if (newGame && newGame !== game.value) {
    game.value = newGame as string
    fetchVideos()
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})

// Ajouter la notification pour les favoris
const toggleFavoriteWithNotification = (game: string) => {
  toggleFavorite(game)
  const message = isFavorite(game) 
    ? `${game} has been added to favorites`
    : `${game} has been removed from favorites`
  toast.success(message)
}

// Expose les méthodes pour les tests
defineExpose({
  updateFilters,
  updateSort,
  fetchVideos,
  setupIntersectionObserver,
  retrySearch,
  toggleFavoriteWithNotification,
  // formatViews and formatDurationForDisplay are now imported, no need to expose if not directly called by parent/test on instance
  searchQuery,
  handleSearch
})
</script> 