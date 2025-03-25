<template>
  <div class="video-list">
    <h1 class="text-3xl font-bold mb-6 text-white">Vidéos {{ currentGame }}</h1>
    <TwitchVideoGrid :videos="videos" v-if="videos.length > 0" />
    <div v-else class="flex items-center justify-center h-64 text-gray-400">
      <p class="text-xl">Aucune vidéo trouvée</p>
    </div>
  </div>
</template>

<script>
import TwitchVideoGrid from '@/components/TwitchVideoGrid.vue'
import { useVideoStore } from '@/stores/videoStore'
import { onMounted, ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'VideoList',
  components: {
    TwitchVideoGrid
  },
  setup() {
    const videoStore = useVideoStore()
    const route = useRoute()
    const currentGame = ref('')

    // Charger le script Twitch
    onMounted(() => {
      const script = document.createElement('script')
      script.src = 'https://player.twitch.tv/js/embed/v1.js'
      document.head.appendChild(script)
    })

    // Observer les changements de route
    watch(() => route.params.game, async (newGame) => {
      if (newGame) {
        currentGame.value = newGame
        await videoStore.searchVideos({ game_name: newGame })
      }
    }, { immediate: true })

    return {
      videos: computed(() => videoStore.videos),
      currentGame
    }
  }
}
</script>

<style scoped>
.video-list {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8;
}
</style> 