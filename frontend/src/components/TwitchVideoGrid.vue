<template>
  <div class="videos-container">
    <a
      v-for="video in videos"
      :key="video.id"
      :href="`https://twitch.tv/${video.user_name}`"
      target="_blank"
      rel="noopener noreferrer"
      class="video-card"
    >
      <div class="video-wrapper">
        <div class="thumbnail-container">
          <img
            :src="`https://static-cdn.jtvnw.net/previews-ttv/live_user_${video.user_name.toLowerCase()}-214x120.jpg`"
            :alt="video.title"
            class="thumbnail"
            @error="handleImageError"
            loading="lazy"
          />
          <div class="video-overlay">
            <div class="play-button">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="play-icon">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </div>
            <div class="video-duration" v-if="video.duration">
              {{ formatDuration(video.duration) }}
            </div>
          </div>
        </div>
      </div>
      <div class="video-details">
        <h3 class="video-title">{{ video.title }}</h3>
        <div class="video-meta">
          <p class="video-streamer">{{ video.user_name }}</p>
          <p class="video-views">{{ formatViews(video.view_count) }} vues</p>
        </div>
      </div>
    </a>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  videos: {
    type: Array,
    required: true
  }
})

// Log temporaire pour débugger
watch(() => props.videos, (videos) => {
  videos.forEach(video => {
    const thumbnailUrl = `https://static-cdn.jtvnw.net/previews-ttv/live_user_${video.user_name.toLowerCase()}-214x120.jpg`
    console.log('URL miniature pour', video.user_name, ':', thumbnailUrl)
  })
}, { immediate: true })

const handleImageError = (event) => {
  event.target.src = '/placeholder-video.jpg'
}

const formatViews = (views) => {
  if (!views) return '0 vue'
  if (views >= 1000000) {
    return `${(views / 1000000).toFixed(1)}M vues`
  }
  if (views >= 1000) {
    return `${(views / 1000).toFixed(1)}k vues`
  }
  return `${views} vue${views > 1 ? 's' : ''}`
}

const formatDuration = (duration) => {
  if (!duration) return ''
  const matches = duration.match(/(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?/)
  if (!matches) return ''

  const hours = parseInt(matches[1] || 0)
  const minutes = parseInt(matches[2] || 0)
  const seconds = parseInt(matches[3] || 0)

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.videos-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.video-card {
  background: #18181b;
  border-radius: 0.5rem;
  overflow: hidden;
  transition: transform 0.2s;
  text-decoration: none;
  display: block;
}

.video-card:hover {
  transform: translateY(-2px);
}

.thumbnail-container {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 Aspect Ratio */
  background: #0e0e10;
}

.thumbnail {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumbnail-container:hover .video-overlay {
  opacity: 1;
}

.play-button {
  width: 48px;
  height: 48px;
  color: white;
}

.play-icon {
  width: 100%;
  height: 100%;
}

.video-duration {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.video-details {
  padding: 1rem;
}

.video-title {
  color: white;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.video-streamer {
  color: #a970ff;
  font-size: 0.875rem;
}

.video-views {
  color: #adadb8;
  font-size: 0.875rem;
}

@media (max-width: 640px) {
  .videos-container {
    gap: 1rem;
    padding: 1rem;
  }
}
</style> 