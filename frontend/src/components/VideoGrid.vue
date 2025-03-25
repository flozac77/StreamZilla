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
          @click="videoStore.searchVideos(videoStore.currentSearch)"
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
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-6"
      v-intersection="handleIntersection"
    >
      <VideoCard
        v-for="video in videoStore.videos"
        :key="video.id"
        :title="video.title"
        :thumbnail="video.thumbnail_url"
        :author="video.user_name"
        :views="video.view_count"
        :date="video.created_at"
        :duration="video.duration"
      />

      <div v-if="videoStore.loading" class="col-span-full text-center py-4">
        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-twitch-purple mx-auto"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useVideoStore } from '../stores/videoStore'
import VideoCard from './VideoCard.vue'
import { vIntersection } from '@vueuse/components'

const videoStore = useVideoStore()

const handleIntersection = ([entry]) => {
  if (entry.isIntersecting && !videoStore.loading && videoStore.hasMore) {
    videoStore.loadMore()
  }
}
</script> 