<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Filtres -->
    <SearchFilters
      @update:filters="updateFilters"
      @update:sort="updateSort"
    />

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-purple-500"></div>
    </div>
    
    <div v-else-if="error" class="text-center text-red-500">
      {{ error }}
    </div>
    
    <div v-else>
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-white">
          Vidéos {{ game }}
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
          {{ isFavorite(game) ? 'Retirer des favoris' : 'Ajouter aux favoris' }}
        </button>
      </div>

      <!-- Composant UserPreferences -->
      <UserPreferences class="mb-8" />
      
      <!-- Grille de vidéos -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="video in videoStore.visibleVideos" :key="video.id" 
             class="bg-gray-800 rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
          <div class="relative group">
            <img :src="`https://static-cdn.jtvnw.net/previews-ttv/live_user_${video.user_name.toLowerCase()}-640x360.jpg`"
                 :alt="video.title"
                 class="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105">
            
            <!-- Overlay au survol -->
            <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
              <div class="text-white text-center">
                <span class="bg-purple-600 px-2 py-1 rounded text-sm">
                  {{ formatDuration(video.duration) }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="p-4">
            <h2 class="text-xl font-semibold mb-2 line-clamp-2 text-white">{{ video.title }}</h2>
            <p class="text-purple-400 mb-2">{{ video.user_name }}</p>
            <p class="text-gray-400 text-sm">{{ formatViews(video.view_count) }} vues • {{ formatDuration(video.duration) }}</p>
          </div>
          
          <div class="px-4 pb-4">
            <a :href="video.url" 
               target="_blank"
               class="inline-block bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors duration-300">
              Voir sur Twitch
            </a>
          </div>
        </div>
      </div>

      <!-- Loader et trigger pour le scrolling infini -->
      <div ref="loadMoreTrigger" 
           class="flex justify-center py-8 mt-4">
        <template v-if="videoStore.loading || videoStore.loadingMore">
          <LoadingSpinner :message="videoStore.loadingMore ? 'Chargement de plus de vidéos...' : 'Chargement des vidéos...'" />
        </template>
        <template v-else-if="!videoStore.hasMore && videoStore.visibleVideos.length > 0">
          <p class="text-gray-500">Plus de vidéos disponibles</p>
        </template>
      </div>

      <!-- Message d'erreur -->
      <div v-if="videoStore.error" 
           class="text-center py-4 text-red-500">
        {{ videoStore.error }}
        <button @click="retrySearch" 
                class="ml-2 text-blue-500 hover:underline">
          Réessayer
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, defineExpose } from 'vue'
import { useRoute } from 'vue-router'
import { useVideoStore } from '../stores/videoStore'
import { useUserPreferencesStore } from '../stores/userPreferences'
import SearchFilters from '../components/SearchFilters.vue'
import UserPreferences from '../components/UserPreferences.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import { useIntersectionObserver } from '@vueuse/core'
import { useToast } from 'vue-toastification'

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

// Filtres et tri
const activeFilters = ref({
  date: 'all',
  duration: 'all',
  views: 'all'
})
const activeSort = ref('date')

const updateFilters = (newFilters: any) => {
  activeFilters.value = newFilters
}

const updateSort = (newSort: string) => {
  activeSort.value = newSort
}

// Configuration de l'Intersection Observer avec des options plus sensibles
const setupIntersectionObserver = () => {
  if (!loadMoreTrigger.value) return

  const observer = useIntersectionObserver(
    loadMoreTrigger,
    ([entry]) => {
      if (entry.isIntersecting && !videoStore.loading && !videoStore.loadingMore) {
        console.log('🔄 Intersection détectée, chargement de plus de vidéos...')
        videoStore.loadMore()
      }
    },
    {
      threshold: 0.1,
      rootMargin: '100px'
    }
  )

  return observer
}

// Gestion du chargement initial
const fetchVideos = async () => {
  try {
    loading.value = true
    error.value = ''
    await videoStore.searchVideosByGame(game.value)
    addToHistory(game.value)
  } catch (e) {
    error.value = "Une erreur est survenue lors du chargement des vidéos"
    toast.error(error.value)
    console.error('Erreur dans fetchVideos:', e)
  } finally {
    loading.value = false
  }
}

// Réessayer en cas d'erreur
const retrySearch = () => {
  videoStore.resetSearch()
  fetchVideos()
}

// Initialisation
onMounted(() => {
  videoStore.resetSearch() // S'assure qu'on part d'un état propre
  fetchVideos()
  setupIntersectionObserver()
  startAutoRefresh()
})

// Configuration du rechargement automatique
const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshInterval.value = window.setInterval(() => {
    console.log('Rechargement automatique des vidéos...')
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
    videoStore.resetSearch()
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
    ? `${game} a été ajouté aux favoris`
    : `${game} a été retiré des favoris`
  toast.success(message)
}

const formatViews = (views: number): string => {
  if (views >= 1000000) {
    return `${(views / 1000000).toFixed(1)}M`
  } else if (views >= 1000) {
    return `${(views / 1000).toFixed(1)}k`
  }
  return views.toString()
}

const formatDuration = (duration: string): string => {
  const matches = duration.match(/(\d+h)?(\d+m)?(\d+s)?/)
  if (!matches) return duration
  
  const hours = matches[1] ? matches[1].replace('h', '') : '0'
  const minutes = matches[2] ? matches[2].replace('m', '') : '0'
  const seconds = matches[3] ? matches[3].replace('s', '') : '0'
  
  if (hours !== '0') {
    return `${hours}:${minutes.padStart(2, '0')}:${seconds.padStart(2, '0')}`
  }
  return `${minutes}:${seconds.padStart(2, '0')}`
}

// Expose les méthodes pour les tests
defineExpose({
  updateFilters,
  updateSort,
  fetchVideos,
  setupIntersectionObserver,
  retrySearch,
  toggleFavoriteWithNotification,
  formatViews,
  formatDuration
})
</script> 