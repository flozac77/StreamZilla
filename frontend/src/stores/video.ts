import { defineStore } from 'pinia'
import axios from 'axios'

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

interface SearchResponse {
  game_name: string
  game: Game | null
  videos: Video[]
  total_count: number
  last_updated: string
}

interface VideoResponse {
  videos: Video[]
  game: string
  last_updated: string
}

interface VideoState {
  allVideos: Video[]
  visibleVideos: Video[]
  loading: boolean
  error: string | null
  currentGame: string
  hasMore: boolean
  totalCount: number
  page: number
  itemsPerPage: number
  retryCount: number
  lastError: Error | null
  loadingMore: boolean
  filters: {
    date: string
    duration: string
    views: string
    language: string
  }
  sortBy: string
}

export const useVideoStore = defineStore('video', {
  state: (): VideoState => ({
    allVideos: [],
    visibleVideos: [],
    loading: false,
    loadingMore: false,
    error: null,
    currentGame: '',
    hasMore: true,
    totalCount: 0,
    page: 1,
    itemsPerPage: 12,
    retryCount: 0,
    lastError: null,
    filters: {
      date: 'all',
      duration: 'all',
      views: 'all',
      language: 'all'
    },
    sortBy: 'date'
  }),

  getters: {
    filteredVideos(): Video[] {
      let filtered = [...this.allVideos]

      // Filtre par date
      if (this.filters.date !== 'all') {
        // En test, on utilise une date fixe
        const now = import.meta.env.MODE === 'test' 
          ? new Date('2024-01-01T12:00:00Z')
          : new Date()
        
        const timeMap = {
          'today': 24 * 60 * 60 * 1000,
          'this_week': 7 * 24 * 60 * 60 * 1000,
          'this_month': 30 * 24 * 60 * 60 * 1000
        }
        
        if (timeMap[this.filters.date as keyof typeof timeMap]) {
          const timeLimit = timeMap[this.filters.date as keyof typeof timeMap]
          filtered = filtered.filter(video => {
            const videoDate = new Date(video.created_at)
            return (now.getTime() - videoDate.getTime()) <= timeLimit
          })
        }
      }

      // Filtre par durée
      if (this.filters.duration !== 'all') {
        const getDurationInSeconds = (duration: string) => {
          const matches = duration.match(/(\d+h)?(\d+m)?(\d+s)?/)
          if (!matches) return 0
          
          const hours = parseInt(matches[1]?.replace('h', '') || '0') * 3600
          const minutes = parseInt(matches[2]?.replace('m', '') || '0') * 60
          const seconds = parseInt(matches[3]?.replace('s', '') || '0')
          
          return hours + minutes + seconds
        }

        const durationMap = {
          'short': { min: 0, max: 15 * 60 }, // moins de 15 minutes
          'medium': { min: 15 * 60, max: 60 * 60 }, // 15-60 minutes
          'long': { min: 60 * 60, max: Infinity } // plus de 60 minutes
        }

        const range = durationMap[this.filters.duration as keyof typeof durationMap]
        if (range) {
          filtered = filtered.filter(video => {
            const duration = getDurationInSeconds(video.duration)
            return duration >= range.min && duration < range.max
          })
        }
      }

      // Filtre par vues
      if (this.filters.views !== 'all') {
        const viewsMap = {
          'less_100': { min: 0, max: 100 },
          '100_1000': { min: 100, max: 1000 },
          'more_1000': { min: 1000, max: Infinity }
        }

        const range = viewsMap[this.filters.views as keyof typeof viewsMap]
        if (range) {
          filtered = filtered.filter(video => 
            video.view_count >= range.min && video.view_count < range.max
          )
        }
      }

      // Filtre par langue
      if (this.filters.language !== 'all') {
        filtered = filtered.filter(video => video.language === this.filters.language)
      }

      // Tri des vidéos
      switch (this.sortBy) {
        case 'date':
          filtered.sort((a, b) => {
            const dateA = new Date(a.created_at)
            const dateB = new Date(b.created_at)
            return dateB.getTime() - dateA.getTime()
          })
          break
        case 'views':
          filtered.sort((a, b) => b.view_count - a.view_count)
          break
        case 'duration':
          filtered.sort((a, b) => {
            const getDuration = (d: string) => {
              const matches = d.match(/(\d+h)?(\d+m)?(\d+s)?/)
              if (!matches) return 0
              const h = parseInt(matches[1]?.replace('h', '') || '0') * 3600
              const m = parseInt(matches[2]?.replace('m', '') || '0') * 60
              const s = parseInt(matches[3]?.replace('s', '') || '0')
              return h + m + s
            }
            return getDuration(b.duration) - getDuration(a.duration)
          })
          break
      }

      return filtered
    }
  },

  actions: {
    updateFilters(newFilters: Partial<VideoState['filters']>) {
      this.filters = { ...this.filters, ...newFilters }
      this.applyFilters()
    },

    updateSort(newSort: string) {
      this.sortBy = newSort
      this.applyFilters()
    },

    applyFilters() {
      // Applique les filtres et met à jour visibleVideos
      const filtered = this.filteredVideos
      this.visibleVideos = filtered.slice(0, this.itemsPerPage)
      this.totalCount = filtered.length
      this.hasMore = this.visibleVideos.length < filtered.length
    },

    async searchVideosByGame(game: string, append: boolean = false): Promise<SearchResponse> {
      if (!append) {
        this.loading = true
      } else {
        this.loadingMore = true
      }
      
      this.error = null
      this.lastError = null
      
      try {
        console.log('🔍 Recherche de vidéos:', { 
          game, 
          page: this.page,
          append,
          existingVideos: this.allVideos.length 
        })
        
        const response = await api.get<SearchResponse>('/api/search', {
          params: {
            game,
            page: this.page,
            limit: 100
          }
        })

        if (!response.data?.videos) {
          throw new Error('Format de réponse invalide')
        }

        // Déduplique les vidéos
        const newVideos = response.data.videos.filter(newVideo => 
          !this.allVideos.some(existing => existing.id === newVideo.id)
        )

        if (append) {
          this.allVideos = [...this.allVideos, ...newVideos]
        } else {
          this.allVideos = newVideos
        }

        this.applyFilters()
        this.currentGame = game
        this.totalCount = response.data.total_count || 0
        this.hasMore = this.allVideos.length < this.totalCount
        this.retryCount = 0 // Reset le compteur d'erreurs en cas de succès
        
        return response.data

      } catch (error: any) {
        this.lastError = error
        this.error = error instanceof Error ? error.message : 'Une erreur est survenue'
        this.retryCount++
        
        console.error('❌ Erreur lors du chargement des vidéos:', {
          error,
          retryCount: this.retryCount,
          page: this.page,
          game
        })

        // Si on a moins de 3 tentatives, on réessaie après un délai
        if (this.retryCount < 3) {
          await new Promise(resolve => setTimeout(resolve, 1000 * this.retryCount))
          return this.searchVideosByGame(game, append)
        }

        throw error
      } finally {
        if (!append) {
          this.loading = false
        } else {
          this.loadingMore = false
        }
      }
    },

    async loadMoreVideos() {
      if (this.loading || this.loadingMore) return

      const filtered = this.filteredVideos
      const currentLength = this.visibleVideos.length
      const remainingVideos = filtered.slice(
        currentLength,
        currentLength + this.itemsPerPage
      )

      if (remainingVideos.length > 0) {
        this.visibleVideos = [...this.visibleVideos, ...remainingVideos]
        this.hasMore = currentLength + remainingVideos.length < filtered.length
        return
      }

      if (this.allVideos.length < this.totalCount) {
        this.page++
        await this.searchVideosByGame(this.currentGame, true)
      } else {
        this.hasMore = false
      }
    },

    resetSearch() {
      console.log('🔄 Réinitialisation de la recherche')
      this.allVideos = []
      this.visibleVideos = []
      this.hasMore = true
      this.totalCount = 0
      this.currentGame = ''
      this.error = null
      this.page = 1
      this.retryCount = 0
      this.lastError = null
      this.loading = false
      this.loadingMore = false
      this.filters = {
        date: 'all',
        duration: 'all',
        views: 'all',
        language: 'all'
      }
      this.sortBy = 'date'
    }
  }
}) 