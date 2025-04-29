<template>
  <div class="min-h-screen bg-gray-100">
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-2xl mx-auto">
        <h1 class="text-4xl font-bold text-center mb-8 text-gray-800">
          Rechercher des vidéos Twitch
        </h1>
        
        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher un jeu..."
              class="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              @keyup.enter="handleSearch"
            >
            <button
              @click="handleSearch"
              class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors duration-300"
            >
              Rechercher
            </button>
          </div>
        </div>

        <div class="mt-8">
          <h2 class="text-2xl font-semibold mb-4 text-gray-800">Jeux populaires</h2>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <router-link
              v-for="game in popularGames"
              :key="game.id"
              :to="{ name: 'videos', params: { game: game.name }}"
              class="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300"
            >
              <img :src="game.boxArtUrl.replace('{width}x{height}', '285x380')" :alt="game.name" class="w-full h-40 object-cover">
              <div class="p-4">
                <h3 class="font-semibold text-gray-800">{{ game.name }}</h3>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')

const popularGames = ref([
  {
    id: '27471',
    name: 'Minecraft',
    boxArtUrl: 'https://static-cdn.jtvnw.net/ttv-boxart/27471-{width}x{height}.jpg'
  },
  {
    id: '21779',
    name: 'League of Legends',
    boxArtUrl: 'https://static-cdn.jtvnw.net/ttv-boxart/21779-{width}x{height}.jpg'
  },
  {
    id: '33214',
    name: 'Fortnite',
    boxArtUrl: 'https://static-cdn.jtvnw.net/ttv-boxart/33214-{width}x{height}.jpg'
  },
  {
    id: '32982',
    name: 'Grand Theft Auto V',
    boxArtUrl: 'https://static-cdn.jtvnw.net/ttv-boxart/32982-{width}x{height}.jpg'
  }
])

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ name: 'videos', params: { game: searchQuery.value.trim() }})
  }
}
</script> 