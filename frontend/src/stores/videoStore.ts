import { defineStore } from 'pinia'
import axios from 'axios'
import { parseDuration } from '@/utils/duration'
import type { Video, VideoState, SearchParams } from '@/types/video'
import type { VideoFilters, SortOption } from '@/types/filters'
import { DEFAULT_FILTERS, DEFAULT_SORT } from '@/types/filters'

export const useVideoStore = defineStore('video', {
  state: (): VideoState => ({
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
    filters: { ...DEFAULT_FILTERS },
    sortBy: DEFAULT_SORT
  }),

  getters: {
    filteredVideos(state): Video[] {
      let filtered = [...state.videos]

      // Filtre par date
      if (state.filters.date !== 'all') {
        const now = new Date()
        const cutoff = new Date()
        switch (state.filters.date) {
          case 'today':
            cutoff.setDate(now.getDate() - 1)
            break
          case 'this_week':
            cutoff.setDate(now.getDate() - 7)
            break
          case 'this_month':
            cutoff.setMonth(now.getMonth() - 1)
            break
        }
        filtered = filtered.filter(video => new Date(video.created_at) >= cutoff)
      }

      // Filtre par durée
      if (state.filters.duration !== 'all') {
        filtered = filtered.filter(video => {
          const duration = parseDuration(video.duration)
          switch (state.filters.duration) {
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
      if (state.filters.views !== 'all') {
        filtered = filtered.filter(video => {
          switch (state.filters.views) {
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
      if (state.filters.language !== 'all') {
        filtered = filtered.filter(video => video.language === state.filters.language)
      }

      // Tri
      filtered.sort((a, b) => {
        switch (state.sortBy) {
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

      return filtered
    }
  },

  actions: {
    updateFilters(newFilters: Partial<VideoFilters>) {
      this.filters = {
        ...this.filters,
        ...newFilters
      }
      this.applyFilters()
    },

    updateSort(sort: SortOption) {
      this.sortBy = sort
      this.applyFilters()
    },

    reset() {
      this.videos = []
      this.allVideos = []
      this.visibleVideos = []
      this.loading = false
      this.loadingMore = false
      this.error = null
      this.currentSearch = ''
      this.currentGame = ''
      this.page = 1
      this.hasMore = true
      this.filters = { ...DEFAULT_FILTERS }
      this.sortBy = DEFAULT_SORT
    },

    applyFilters() {
      this.visibleVideos = this.filteredVideos
    },

    async searchVideosByGame(game_name: string) {
      try {
        this.loading = true
        this.error = null
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/search`, {
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
        console.error('Error fetching videos:', error)
        this.error = 'Une erreur est survenue lors de la recherche des vidéos'
        this.videos = []
        this.allVideos = []
        this.visibleVideos = []
      } finally {
        this.loading = false
      }
    },

    async searchVideos(params: SearchParams) {
      try {
        if (params.reset) {
          this.loading = true
          this.page = 1
        } else {
          this.loadingMore = true
          this.page += 1
        }
        this.error = null

        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/search`, {
          params: {
            game: params.game_name,
            limit: params.limit || 10,
            page: this.page,
            use_cache: true
          }
        })

        const newVideos = response.data.videos || []
        this.videos = params.reset ? newVideos : [...this.videos, ...newVideos]
        this.allVideos = params.reset ? newVideos : [...this.allVideos, ...newVideos]
        this.currentGame = params.game_name
        this.currentSearch = params.game_name
        this.hasMore = newVideos.length === (params.limit || 10)
        this.applyFilters()
      } catch (error) {
        console.error('Error fetching videos:', error)
        this.error = 'Une erreur est survenue lors du chargement des vidéos'
        if (params.reset) {
          this.videos = []
          this.allVideos = []
          this.visibleVideos = []
        }
      } finally {
        if (params.reset) {
          this.loading = false
        } else {
          this.loadingMore = false
        }
      }
    },

    async loadMore() {
      if (this.loading || this.loadingMore || !this.hasMore) return

      await this.searchVideos({
        game_name: this.currentGame,
        limit: 10,
        reset: false
      })
    }
  }
}) 