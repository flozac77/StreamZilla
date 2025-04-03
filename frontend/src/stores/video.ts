import { defineStore } from 'pinia'
import axios from 'axios'
import type { VideoState, VideoStoreActions, SearchParams, SearchResponse } from '../types/video'
import type { VideoFilters, SortOption, FilterChangeEvent } from '../types/filters'
import { DEFAULT_FILTERS, DEFAULT_SORT } from '../types/filters'
import { parseDuration } from '../utils/duration'

// Créer une instance axios avec la configuration de base
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
})

interface Video {
  id: string
  user_name: string
  title: string
  url: string
  view_count: number
  duration: string
  created_at: string
  language: string
  thumbnail_url: string
  description: string
  streamer_name: string
  game_id: string
  game_name: string
}

interface Game {
  id: string
  name: string
  box_art_url: string
}

interface ApiResponse<T> {
  data: T
  status: number
  statusText: string
  headers: Record<string, string>
  config: any
  request: any
}

interface VideoResponse {
  videos: Video[]
  game: string
  last_updated: string
}

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

  getters: {
    filteredVideos(): Video[] {
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
          const duration = this.parseDuration(video.duration)
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
            return this.parseDuration(b.duration) - this.parseDuration(a.duration)
          default:
            return 0
        }
      })

      return filtered
    }
  },

  actions: {
    async searchVideosByGame(game_name: string): Promise<void> {
      return this.searchVideos({ game_name, reset: true })
    },

    async searchVideos({ game_name, limit = 10, page = 1, reset = false }: SearchParams): Promise<void> {
      if (reset) {
        this.videos = []
        this.allVideos = []
        this.visibleVideos = []
        this.page = 1
        this.hasMore = true
      }
      
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get<SearchResponse>(`/api/search`, {
          params: {
            game_name,
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
        
        // Applique les filtres actuels aux nouvelles vidéos
        this.applyFilters()
        
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Une erreur est survenue'
      } finally {
        this.loading = false
      }
    },

    async loadMore(): Promise<void> {
      if (!this.loading && !this.loadingMore && this.hasMore) {
        this.loadingMore = true
        this.page++
        await this.searchVideos({
          game_name: this.currentSearch,
          page: this.page
        })
        this.loadingMore = false
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
    },

    parseDuration(duration: string): number {
      const matches = duration.match(/(\d+)h(\d+)m/)
      if (!matches) return 0
      const [_, hours, minutes] = matches
      return parseInt(hours) * 3600 + parseInt(minutes) * 60
    }
  }
}) 