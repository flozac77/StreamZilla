<template>
  <div class="bg-gray-800 p-4 rounded-lg shadow-lg mb-6">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- Date -->
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Date</label>
        <select 
          v-model="filters.date"
          class="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500"
          data-test="date-filter"
        >
          <option value="all">Toutes les dates</option>
          <option value="today">Aujourd'hui</option>
          <option value="this_week">Cette semaine</option>
          <option value="this_month">Ce mois</option>
        </select>
      </div>

      <!-- Durée -->
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Durée</label>
        <select 
          v-model="filters.duration"
          class="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500"
          data-test="duration-filter"
        >
          <option value="all">Toutes les durées</option>
          <option value="short">Moins de 15 minutes</option>
          <option value="medium">15-60 minutes</option>
          <option value="long">Plus de 60 minutes</option>
        </select>
      </div>

      <!-- Vues -->
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Vues</label>
        <select 
          v-model="filters.views"
          class="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500"
          data-test="views-filter"
        >
          <option value="all">Toutes les vues</option>
          <option value="less_100">Moins de 100</option>
          <option value="100_1000">100-1000</option>
          <option value="more_1000">Plus de 1000</option>
        </select>
      </div>

      <!-- Langue -->
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-2">Langue</label>
        <select 
          v-model="filters.language"
          class="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500"
          data-test="language-filter"
        >
          <option value="all">Toutes les langues</option>
          <option v-for="lang in LANGUAGES" :key="lang.value" :value="lang.value">
            {{ lang.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Boutons de tri -->
    <div class="flex gap-2 mt-4">
      <button 
        v-for="sort in SORT_OPTIONS" 
        :key="sort.value"
        @click="updateSort(sort.value)"
        :class="[
          'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
          sortBy === sort.value
            ? 'bg-purple-600 text-white'
            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
        ]"
        data-test="sort-button"
      >
        {{ sort.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useVideoStore } from '@/stores/videoStore'
import type { VideoFilters, SortOption } from '@/types/filters'

const videoStore = useVideoStore()
const { filters, sortBy } = storeToRefs(videoStore)

const LANGUAGES = [
  { value: 'fr', label: 'Français' },
  { value: 'en', label: 'Anglais' },
  { value: 'es', label: 'Espagnol' },
  { value: 'de', label: 'Allemand' },
  { value: 'it', label: 'Italien' },
  { value: 'pt', label: 'Portugais' },
  { value: 'ru', label: 'Russe' },
  { value: 'ja', label: 'Japonais' },
  { value: 'ko', label: 'Coréen' },
  { value: 'zh', label: 'Chinois' }
] as const

const SORT_OPTIONS = [
  { value: 'date', label: 'Date' },
  { value: 'views', label: 'Vues' },
  { value: 'duration', label: 'Durée' }
] as const

const updateSort = (sort: SortOption) => {
  videoStore.updateSort(sort)
}
</script> 