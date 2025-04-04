<template>
  <div class="relative group">
    <img v-show="isLoaded"
         :src="currentUrl"
         :alt="alt"
         class="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105"
         @error="handleError"
         @load="handleLoad">
    
    <!-- Placeholder -->
    <div v-show="!isLoaded" 
         class="absolute inset-0 bg-gray-700 animate-pulse flex items-center justify-center">
      <span class="material-icons text-4xl text-gray-500">videocam</span>
    </div>

    <!-- Hover Overlay -->
    <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
      <div class="text-white text-center">
        <slot name="overlay"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = defineProps<{
  username: string
  alt: string
}>()

const isLoaded = ref(false)
const currentUrl = ref('')
const retryCount = ref(0)

// Différentes stratégies de génération d'URL pour Twitch
const URL_STRATEGIES = [
  (username: string) => `https://static-cdn.jtvnw.net/previews-ttv/live_user_${username.toLowerCase()}-640x360.jpg`,
  (username: string) => `https://static-cdn.jtvnw.net/jtv_user_pictures/${username.toLowerCase()}-profile_image-300x300.jpg`,
  (username: string) => `https://static-cdn.jtvnw.net/ttv-boxart/${username.toLowerCase()}-640x360.jpg`,
  () => '/placeholder-video.png'
]

const handleError = async () => {
  if (retryCount.value >= URL_STRATEGIES.length - 1) {
    currentUrl.value = URL_STRATEGIES[URL_STRATEGIES.length - 1](props.username)
    isLoaded.value = true
    return
  }
  
  retryCount.value++
  currentUrl.value = URL_STRATEGIES[retryCount.value](props.username)
}

const handleLoad = () => {
  isLoaded.value = true
}

const resetImage = () => {
  isLoaded.value = false
  retryCount.value = 0
  currentUrl.value = URL_STRATEGIES[0](props.username)
}

// Réinitialiser l'image quand le username change
watch(() => props.username, resetImage)

onMounted(resetImage)
</script> 