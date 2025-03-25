<template>
  <div class="bg-twitch-light rounded-lg overflow-hidden shadow-lg transition-transform hover:scale-105">
    <div class="relative aspect-video">
      <img
        v-lazy="thumbnail"
        :alt="title"
        class="w-full h-full object-cover"
      />
      <div class="absolute bottom-2 right-2 bg-black bg-opacity-80 px-2 py-1 rounded text-sm text-white">
        {{ formatDuration(duration) }}
      </div>
    </div>
    
    <div class="p-4">
      <h3 class="text-twitch-text font-semibold text-lg line-clamp-2" :title="title">
        {{ title }}
      </h3>
      
      <div class="mt-2 text-gray-400 text-sm">
        <p class="flex items-center">
          <span class="mr-2">{{ author }}</span>
          <span class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
            </svg>
            {{ formatViews(views) }}
          </span>
        </p>
        
        <p class="mt-1">
          {{ formatDate(date) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  thumbnail: {
    type: String,
    required: true
  },
  author: {
    type: String,
    required: true
  },
  views: {
    type: Number,
    required: true
  },
  date: {
    type: String,
    required: true
  },
  duration: {
    type: String,
    required: true
  }
})

const formatDuration = (duration) => {
  // Format: "1h2m3s" to "1:02:03"
  const matches = duration.match(/(\d+h)?(\d+m)?(\d+s)?/)
  const hours = matches[1] ? parseInt(matches[1]) : 0
  const minutes = matches[2] ? parseInt(matches[2]) : 0
  const seconds = matches[3] ? parseInt(matches[3]) : 0
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

const formatViews = (views) => {
  if (views >= 1000000) {
    return `${(views / 1000000).toFixed(1)}M vues`
  }
  if (views >= 1000) {
    return `${(views / 1000).toFixed(1)}k vues`
  }
  return `${views} vues`
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 