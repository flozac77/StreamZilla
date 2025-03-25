<template>
  <div class="container mx-auto px-4 py-8">
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-purple-500"></div>
    </div>
    
    <div v-else-if="error" class="text-center text-red-500">
      {{ error }}
    </div>
    
    <div v-else>
      <h1 class="text-3xl font-bold mb-8 text-center text-white">
        Vidéos {{ game }}
      </h1>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="video in videos" :key="video.id" 
             class="bg-gray-800 rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
          <img :src="`https://static-cdn.jtvnw.net/previews-ttv/live_user_${video.user_name.toLowerCase()}-640x360.jpg`"
               :alt="video.title"
               class="w-full h-48 object-cover">
          
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useVideoStore } from '../stores/video'

// Définition de l'interface Video
interface Video {
  id: string
  user_name: string
  title: string
  url: string
  view_count: number
  duration: string
}

const route = useRoute()
const videoStore = useVideoStore()

const game = ref(route.params.game as string)
const videos = ref<Video[]>([])
const loading = ref(true)
const error = ref('')
const refreshInterval = ref<number | null>(null)

const fetchVideos = async () => {
  try {
    loading.value = true
    error.value = ''
    const response = await videoStore.searchVideosByGame(game.value)
    videos.value = response.videos
  } catch (e) {
    error.value = "Erreur lors du chargement des vidéos"
    console.error(e)
  } finally {
    loading.value = false
  }
}

// Configuration du rechargement automatique
const startAutoRefresh = () => {
  // Arrêt de l'intervalle existant si présent
  stopAutoRefresh()
  
  // Démarrage d'un nouvel intervalle (2 minutes = 120000 ms)
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

watch(() => route.params.game, (newGame) => {
  game.value = newGame as string
  fetchVideos()
  // Redémarrer l'intervalle quand le jeu change
  startAutoRefresh()
})

onMounted(() => {
  fetchVideos()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script> 