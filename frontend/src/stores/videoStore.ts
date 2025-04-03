import { defineStore } from 'pinia'
import type { VideoState, VideoStoreActions, SearchParams } from '../types/video'
import type { FilterChangeEvent, SortOption } from '../types/filters'
import { DEFAULT_FILTERS, DEFAULT_SORT } from '../types/filters'
import { parseDuration } from '../utils/duration'
import { videoApi } from '@/api/config'

export const useVideoStore = defineStore<string, VideoState, {}, VideoStoreActions>('video', {
  state: () => ({
    videos: [],
    allVideos: [],
    visibleVideos: [],
    loading: false,
    loadingMore: false,
    error: null,
    currentSearch: '',
    currentGame: '',
    page: 1,
    hasMore: true,
    filters: DEFAULT_FILTERS,
    sortBy: DEFAULT_SORT
  }),

  actions: {
    async searchVideosByGame(game_name: string) {
      try {
        this.loading = true
        this.error = null
        const response = await videoApi.get('/api/search', {
          params: {
            game: game_name,
            limit: 10,
            page: 1,
            use_cache: true
          }
        })
        const newVideos = response.data.videos || []
        this.videos = newVideos
        this.allVideos = newVideos
        this.currentGame = game_name
        this.currentSearch = game_name
        this.hasMore = newVideos.length === 10
        this.applyFilters()
      } catch (error) {
        this.error = 'Erreur lors de la recherche des vidéos'
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    async searchVideos({ game_name, limit = 10, page = 1, reset = false }: SearchParams) {
      if (reset) {
        this.resetSearch()
      }

      try {
        this.loading = true
        this.error = null
        const response = await videoApi.get('/api/search', {
          params: { 
            game: game_name,
            limit,
            page,
            use_cache: true
          }
        })
        
        const newVideos = response.data.videos || []
        this.videos = reset ? newVideos : [...this.videos, ...newVideos]
        this.allVideos = reset ? newVideos : [...this.allVideos, ...newVideos]
        this.currentGame = game_name
        this.currentSearch = game_name
        this.hasMore = newVideos.length === limit
        
        this.applyFilters()
      } catch (error) {
        this.error = 'Erreur lors de la recherche des vidéos'
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    async loadMore(): Promise<void> {
      if (!this.loading && !this.loadingMore && this.hasMore) {
        this.loadingMore = true
        try {
          this.page++
          await this.searchVideos({
            game_name: this.currentSearch,
            page: this.page
          })
        } finally {
          this.loadingMore = false
        }
      }
    },

    resetSearch(): void {
      this.videos = []
      this.allVideos = []
      this.visibleVideos = []
      this.page = 1
      this.hasMore = true
      this.currentSearch = ''
      this.currentGame = ''
      this.error = null
      this.filters = DEFAULT_FILTERS
      this.sortBy = DEFAULT_SORT
    },

    updateFilters(event: FilterChangeEvent): void {
      this.filters = {
        ...this.filters,
        [event.type]: event.value
      }
      this.applyFilters()
    },

    updateSort(sortBy: SortOption): void {
      this.sortBy = sortBy
      this.applyFilters()
    },

    applyFilters(): void {
      let filtered = [...this.allVideos]

      // Filtre par date
      if (this.filters.date !== 'all') {
        const now = new Date()
        filtered = filtered.filter(video => {
          const videoDate = new Date(video.created_at)
          switch (this.filters.date) {
            case 'today':
              return videoDate.toDateString() === now.toDateString()
            case 'this_week':
              const weekAgo = new Date(now.setDate(now.getDate() - 7))
              return videoDate >= weekAgo
            case 'this_month':
              const monthAgo = new Date(now.setMonth(now.getMonth() - 1))
              return videoDate >= monthAgo
            default:
              return true
          }
        })
      }

      // Filtre par durée
      if (this.filters.duration !== 'all') {
        filtered = filtered.filter(video => {
          const duration = parseDuration(video.duration)
          switch (this.filters.duration) {
            case 'short':
              return duration <= 900 // 15 minutes
            case 'medium':
              return duration > 900 && duration <= 3600 // 15-60 minutes
            case 'long':
              return duration > 3600 // > 60 minutes
            default:
              return true
          }
        })
      }

      // Filtre par vues
      if (this.filters.views !== 'all') {
        filtered = filtered.filter(video => {
          switch (this.filters.views) {
            case 'less_100':
              return video.view_count < 100
            case '100_1000':
              return video.view_count >= 100 && video.view_count < 1000
            case 'more_1000':
              return video.view_count >= 1000
            default:
              return true
          }
        })
      }

      // Filtre par langue
      if (this.filters.language !== 'all') {
        filtered = filtered.filter(video => video.language === this.filters.language)
      }

      // Tri
      filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'date':
            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          case 'views':
            return b.view_count - a.view_count
          case 'duration':
            return parseDuration(b.duration) - parseDuration(a.duration)
          default:
            return 0
        }
      })

      this.visibleVideos = filtered
    }
  }
}) 