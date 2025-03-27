<template>
  <div class="bg-gray-800 p-4 rounded-lg shadow-lg mb-6">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- Date -->
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Date</label>
        <select v-model="selectedFilters.date"
                class="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500">
          <option value="all">Toutes les dates</option>
          <option value="today">Aujourd'hui</option>
          <option value="this_week">Cette semaine</option>
          <option value="this_month">Ce mois</option>
        </select>
      </div>

      <!-- Durée -->
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Durée</label>
        <select v-model="selectedFilters.duration"
                class="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500">
          <option value="all">Toutes les durées</option>
          <option value="short">Moins de 15 minutes</option>
          <option value="medium">15-60 minutes</option>
          <option value="long">Plus de 60 minutes</option>
        </select>
      </div>

      <!-- Vues -->
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Vues</label>
        <select v-model="selectedFilters.views"
                class="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500">
          <option value="all">Toutes les vues</option>
          <option value="less_100">Moins de 100</option>
          <option value="100_1000">100-1000</option>
          <option value="more_1000">Plus de 1000</option>
        </select>
      </div>

      <!-- Langue -->
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Langue</label>
        <select v-model="selectedFilters.language"
                class="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500"
                @change="handleLanguageChange">
          <option value="all">Toutes les langues</option>
          <option value="fr">Français</option>
          <option value="en">Anglais</option>
          <option value="es">Espagnol</option>
          <option value="de">Allemand</option>
          <option value="it">Italien</option>
          <option value="pt">Portugais</option>
          <option value="ru">Russe</option>
          <option value="ja">Japonais</option>
          <option value="ko">Coréen</option>
          <option value="zh">Chinois</option>
        </select>
      </div>
    </div>

    <!-- Boutons de tri -->
    <div class="flex gap-2 mt-4">
      <button v-for="sort in sortOptions" 
              :key="sort.value"
              @click="handleSort(sort.value)"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                currentSort === sort.value
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              ]">
        {{ sort.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useVideoStore } from '../stores/video'

const videoStore = useVideoStore()
const { filters: storeFilters } = storeToRefs(videoStore)

// Initialiser les filtres locaux avec les valeurs du store
const selectedFilters = reactive({
  date: storeFilters.value.date,
  duration: storeFilters.value.duration,
  views: storeFilters.value.views,
  language: storeFilters.value.language
})

const currentSort = ref(videoStore.$state.sortBy)

const sortOptions = [
  { value: 'date', label: 'Date' },
  { value: 'views', label: 'Vues' },
  { value: 'duration', label: 'Durée' }
]

// Gestion du changement de langue
const handleLanguageChange = () => {
  console.log('🌍 Changement de langue:', selectedFilters.language)
  videoStore.$patch((state) => {
    state.filters.language = selectedFilters.language
  })
  videoStore.applyFilters()
}

// Synchronisation bidirectionnelle avec le store
watch(selectedFilters, (newFilters) => {
  console.log('📋 Mise à jour des filtres:', newFilters)
  videoStore.$patch((state) => {
    state.filters = { ...state.filters, ...newFilters }
  })
  videoStore.applyFilters()
}, { deep: true })

// Synchronisation du store vers le composant
watch(() => storeFilters.value, (newFilters) => {
  Object.assign(selectedFilters, newFilters)
}, { deep: true })

// Gestion du tri
const handleSort = (sort: string) => {
  currentSort.value = sort
  console.log('🔄 Mise à jour du tri:', sort)
  videoStore.$patch((state) => {
    state.sortBy = sort
  })
  videoStore.applyFilters()
}
</script> 