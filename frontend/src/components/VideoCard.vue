<template>
  <div 
    class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
    @click="navigateToVideo"
  >
    <div class="relative">
      <img
        :src="thumbnailUrl"
        :alt="video.title"
        class="w-full aspect-video object-cover"
        @error="handleImageError"
      />
      <div class="absolute bottom-2 right-2 bg-black bg-opacity-80 text-white text-sm px-2 py-1 rounded">
        {{ formattedDuration }}
      </div>
    </div>
    
    <div class="p-4">
      <h3 class="text-lg font-semibold line-clamp-2 mb-2" :title="video.title">
        {{ video.title }}
      </h3>
      
      <div class="flex items-center text-sm text-gray-600 mb-2">
        <span class="font-medium">{{ video.user_name }}</span>
        <span class="mx-2">•</span>
        <span>{{ formattedViews }}</span>
      </div>
      
      <div class="text-sm text-gray-500">
        {{ formattedDate }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Video } from '@/types/video'
import { useRouter } from 'vue-router'

const props = defineProps<{
  video: Video
}>()

const emit = defineEmits<{
  (e: 'error', video: Video): void
}>()

const router = useRouter()

const thumbnailUrl = computed(() => {
  return props.video.thumbnail_url || 
    `https://static-cdn.jtvnw.net/previews-ttv/live_user_${props.video.user_name.toLowerCase()}-640x360.jpg`
})

const formattedDuration = computed(() => {
  const matches = props.video.duration.match(/(\d+)h(\d+)m/)
  if (!matches) return props.video.duration
  const [_, hours, minutes] = matches
  return `${hours}:${minutes.padStart(2, '0')}`
})

const formattedViews = computed(() => {
  if (props.video.view_count >= 1000000) {
    return `${(props.video.view_count / 1000000).toFixed(1)}M vues`
  }
  if (props.video.view_count >= 1000) {
    return `${(props.video.view_count / 1000).toFixed(1)}k vues`
  }
  return `${props.video.view_count} vues`
})

const formattedDate = computed(() => {
  const date = new Date(props.video.created_at)
  return new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(date)
})

const handleImageError = () => {
  emit('error', props.video)
}

const navigateToVideo = () => {
  router.push({
    name: 'video',
    params: { id: props.video.id }
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