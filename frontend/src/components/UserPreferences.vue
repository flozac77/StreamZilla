<template>
  <div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-4">
    <!-- Onglets -->
    <div class="flex gap-4 mb-4">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="[
          'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
          activeTab === tab.id
            ? 'bg-purple-600 text-white'
            : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Contenu des onglets -->
    <div v-if="activeTab === 'history'" class="space-y-2">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">Historique de recherche</h3>
        <button 
          @click="clearHistory"
          class="text-sm text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300"
        >
          Effacer l'historique
        </button>
      </div>
      <div v-if="searchHistory.length === 0" class="text-gray-500 dark:text-gray-400 text-center py-4">
        Aucune recherche récente
      </div>
      <div 
        v-for="item in searchHistory" 
        :key="item.timestamp"
        class="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg cursor-pointer"
        @click="$router.push(`/search/${item.query}`)"
      >
        <span class="text-gray-900 dark:text-white">{{ item.query }}</span>
        <span class="text-sm text-gray-500">{{ formatDate(item.timestamp) }}</span>
      </div>
    </div>

    <div v-else-if="activeTab === 'favorites'" class="space-y-2">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Jeux favoris</h3>
      <div v-if="favoriteGames.length === 0" class="text-gray-500 dark:text-gray-400 text-center py-4">
        Aucun jeu favori
      </div>
      <div 
        v-for="game in favoriteGames" 
        :key="game"
        class="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
      >
        <span 
          class="text-gray-900 dark:text-white cursor-pointer"
          @click="$router.push(`/search/${game}`)"
        >
          {{ game }}
        </span>
        <button 
          @click="toggleFavorite(game)"
          class="text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300"
        >
          <span class="sr-only">Retirer des favoris</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserPreferencesStore } from '@/stores/userPreferences'

const userPreferences = useUserPreferencesStore()
const { searchHistory, favoriteGames, clearHistory, toggleFavorite } = userPreferences

const activeTab = ref('history')

const tabs = [
  { id: 'history', label: 'Historique' },
  { id: 'favorites', label: 'Favoris' }
]

const formatDate = (timestamp: number): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

  if (diffInHours < 24) {
    if (diffInHours < 1) {
      const minutes = Math.floor(diffInHours * 60)
      return `Il y a ${minutes} minute${minutes > 1 ? 's' : ''}`
    }
    return `Il y a ${Math.floor(diffInHours)}h`
  }

  return date.toLocaleDateString()
}
</script> 