<template>
  <div class="videos-container">
    <div
      v-for="video in videos"
      :key="video.id"
      class="video-card"
    >
      <div class="video-wrapper">
        <iframe
          :src="`https://player.twitch.tv/?video=${video.id}&parent=localhost&autoplay=false`"
          height="480"
          width="720"
          allowfullscreen
          frameborder="0"
          scrolling="no"
        ></iframe>
      </div>
      <div class="video-details">
        <h3 class="video-title">{{ video.title }}</h3>
        <p class="video-streamer">{{ video.user_name }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  videos: {
    type: Array,
    required: true
  }
})
</script>

<style scoped>
.videos-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.video-card {
  background: #18181b;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
}

.video-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-details {
  padding: 1rem;
}

.video-title {
  color: white;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.video-streamer {
  color: #a970ff;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .videos-container {
    grid-template-columns: 1fr;
  }
}
</style> 