<template>
  <div>
    <div v-if="videoStore.loading && !videoStore.videos.length" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-twitch-purple mx-auto"></div>
      <p class="text-twitch-text mt-4">Chargement des vidéos...</p>
    </div>

    <div v-else-if="videoStore.error" class="text-center py-8">
      <div class="bg-red-500 bg-opacity-10 text-red-500 p-4 rounded-lg max-w-lg mx-auto">
        <p>{{ videoStore.error }}</p>
        <button
          @click="retrySearch"
          class="mt-4 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors"
        >
          Réessayer
        </button>
      </div>
    </div>

    <div v-else-if="!videoStore.videos.length && videoStore.currentSearch" class="text-center py-8">
      <p class="text-twitch-text">Aucune vidéo trouvée pour "{{ videoStore.currentSearch }}"</p>
    </div>

    <div
      v-else
      ref="gridRef"
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-6"
    >
      <VideoCard
        v-for="video in videoStore.visibleVideos"
        :key="video.id"
        :video="video"
        @error="handleVideoError"
      />

      <div 
        v-if="videoStore.loadingMore" 
        class="col-span-full text-center py-4"
      >
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-twitch-purple mx-auto"></div>
      </div>

      <div 
        v-if="!videoStore.loadingMore && videoStore.hasMore"
        ref="loadMoreTrigger" 
        class="h-4"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useVideoStore } from '@/stores/video'
import VideoCard from './VideoCard.vue'
import type { Video } from '@/types/video'

const videoStore = useVideoStore()
const gridRef = ref<HTMLElement | null>(null)
const loadMoreTrigger = ref<HTMLElement | null>(null)
const observer = ref<IntersectionObserver | null>(null)

const retrySearch = async () => {
  if (!videoStore.currentSearch) return
  try {
    await videoStore.searchVideosByGame(videoStore.currentSearch)
  } catch (error) {
    // L'erreur est déjà gérée dans le store
    console.error('Erreur lors de la nouvelle tentative:', error)
  }
}

const handleVideoError = (video: Video) => {
  console.error(`Erreur de chargement de la vidéo ${video.id}`)
  // On pourrait implémenter une logique de retry ou de fallback ici
}

onMounted(() => {
  observer.value = new IntersectionObserver(
    async ([entry]) => {
      if (entry?.isIntersecting && !videoStore.loading && !videoStore.loadingMore && videoStore.hasMore) {
        try {
          await videoStore.loadMore()
        } catch (error) {
          console.error('Erreur lors du chargement de plus de vidéos:', error)
        }
      }
    },
    {
      rootMargin: '100px',
      threshold: 0.1
    }
  )

  if (loadMoreTrigger.value) {
    observer.value.observe(loadMoreTrigger.value)
  }
})

onUnmounted(() => {
  if (observer.value) {
    observer.value.disconnect()
  }
})
</script> 